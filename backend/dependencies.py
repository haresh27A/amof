"""
FastAPI Dependency Injection Helpers
Component Tag: [A. Infrastructure API]
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from database.session import get_db
from amora.router import AMORARouter
from metadata.repository import MetadataRepository
from evaluation.benchmark import BenchmarkSuite

def get_metadata_repo(db: Session = Depends(get_db)) -> MetadataRepository:
    return MetadataRepository(db)

def get_amora_router(db: Session = Depends(get_db)) -> AMORARouter:
    return AMORARouter(db)

def get_benchmark_suite(db: Session = Depends(get_db)) -> BenchmarkSuite:
    return BenchmarkSuite(db)
