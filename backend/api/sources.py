"""
FastAPI Source Management Endpoints
Component Tag: [A. Source Management API]
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import SourceModel, SourceQualityModel
from metadata.generator import MetadataGenerator
from metadata.repository import MetadataRepository
from backend.dependencies import get_metadata_repo

router = APIRouter(prefix="/sources", tags=["Sources"])

class SourceRegisterRequest(BaseModel):
    source_id: str
    name: str
    source_type: str
    domain: str
    description: str
    endpoint_or_schema: str
    tool_type: Optional[str] = None
    reliability: float = 1.0
    cost: float = 0.05
    latency: float = 0.10
    availability: float = 0.99

class SourceResponse(BaseModel):
    source_id: str
    name: str
    type: str
    domain: str
    description: Optional[str]
    capabilities: Optional[str]
    tool_type: str
    endpoint_or_schema: Optional[str]
    active: bool
    quality: Optional[Dict[str, Any]] = None

@router.post("/register", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def register_source(req: SourceRegisterRequest, repo: MetadataRepository = Depends(get_metadata_repo)):
    """
    POST /sources/register
    Automatically extracts offline metadata, generates vector embeddings, and registers the source.
    """
    meta_dict = MetadataGenerator.generate_source_metadata(
        source_id=req.source_id,
        name=req.name,
        source_type=req.source_type,
        domain=req.domain,
        description=req.description,
        endpoint_or_schema=req.endpoint_or_schema,
        tool_type=req.tool_type,
        reliability=req.reliability,
        cost=req.cost,
        latency=req.latency,
        availability=req.availability
    )

    src_obj = repo.register_source(meta_dict)
    res = repo.get_source_with_quality(src_obj.source_id)
    if not res:
        raise HTTPException(status_code=500, detail="Failed to retrieve registered source.")
    
    src, qual = res
    return SourceResponse(
        source_id=src.source_id,
        name=src.name,
        type=src.type,
        domain=src.domain,
        description=src.description,
        capabilities=src.capabilities,
        tool_type=src.tool_type,
        endpoint_or_schema=src.endpoint_or_schema,
        active=src.active,
        quality={
            "reliability": qual.reliability,
            "freshness": qual.freshness,
            "cost": qual.cost,
            "latency": qual.latency,
            "availability": qual.availability,
            "conflict_rate": qual.conflict_rate,
            "historical_success": qual.historical_success
        } if qual else None
    )

@router.get("", response_model=List[SourceResponse])
def list_sources(repo: MetadataRepository = Depends(get_metadata_repo)):
    """
    GET /sources
    List all active registered sources with quality profiles.
    """
    active_sources = repo.get_all_active_sources()
    output = []
    for src, qual in active_sources:
        output.append(SourceResponse(
            source_id=src.source_id,
            name=src.name,
            type=src.type,
            domain=src.domain,
            description=src.description,
            capabilities=src.capabilities,
            tool_type=src.tool_type,
            endpoint_or_schema=src.endpoint_or_schema,
            active=src.active,
            quality={
                "reliability": qual.reliability,
                "freshness": qual.freshness,
                "cost": qual.cost,
                "latency": qual.latency,
                "availability": qual.availability,
                "conflict_rate": qual.conflict_rate,
                "historical_success": qual.historical_success
            } if qual else None
        ))
    return output

@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: str, repo: MetadataRepository = Depends(get_metadata_repo)):
    """
    GET /sources/{id}
    Retrieve metadata details for a specific source.
    """
    res = repo.get_source_with_quality(source_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found.")
    src, qual = res
    return SourceResponse(
        source_id=src.source_id,
        name=src.name,
        type=src.type,
        domain=src.domain,
        description=src.description,
        capabilities=src.capabilities,
        tool_type=src.tool_type,
        endpoint_or_schema=src.endpoint_or_schema,
        active=src.active,
        quality={
            "reliability": qual.reliability,
            "freshness": qual.freshness,
            "cost": qual.cost,
            "latency": qual.latency,
            "availability": qual.availability,
            "conflict_rate": qual.conflict_rate,
            "historical_success": qual.historical_success
        } if qual else None
    )

@router.post("/{source_id}/refresh", response_model=SourceResponse)
def refresh_source_metadata(source_id: str, repo: MetadataRepository = Depends(get_metadata_repo)):
    """
    POST /sources/{id}/refresh
    Refreshes freshness, availability, and schema summaries while PRESERVING historical success!
    """
    res = repo.get_source_with_quality(source_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found.")
    src, qual = res

    # Regenerate metadata keeping historical_success intact
    hist_succ = qual.historical_success if qual else 1.0

    meta_dict = MetadataGenerator.generate_source_metadata(
        source_id=src.source_id,
        name=src.name,
        source_type=src.type,
        domain=src.domain,
        description=src.description or "",
        endpoint_or_schema=src.endpoint_or_schema or "",
        tool_type=src.tool_type,
        reliability=qual.reliability if qual else 1.0,
        cost=qual.cost if qual else 0.0,
        latency=qual.latency if qual else 0.1,
        availability=qual.availability if qual else 1.0
    )
    meta_dict["quality"]["historical_success"] = hist_succ

    repo.register_source(meta_dict)

    updated_res = repo.get_source_with_quality(source_id)
    u_src, u_qual = updated_res
    return SourceResponse(
        source_id=u_src.source_id,
        name=u_src.name,
        type=u_src.type,
        domain=u_src.domain,
        description=u_src.description,
        capabilities=u_src.capabilities,
        tool_type=u_src.tool_type,
        endpoint_or_schema=u_src.endpoint_or_schema,
        active=u_src.active,
        quality={
            "reliability": u_qual.reliability,
            "freshness": u_qual.freshness,
            "cost": u_qual.cost,
            "latency": u_qual.latency,
            "availability": u_qual.availability,
            "conflict_rate": u_qual.conflict_rate,
            "historical_success": u_qual.historical_success
        } if u_qual else None
    )
