"""
AMORA Database Models (PostgreSQL & SQLite compatible)
Component Tag: [A. Existing/Reused Infrastructure]
"""

from datetime import datetime, timezone
import json
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SourceModel(Base):
    """
    SQLAlchemy model representing standard registered source metadata.
    Tag: [A. Infrastructure]
    """
    __tablename__ = "source"

    source_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(64), nullable=False, index=True)  # sql, api, document, vector, web, kg
    domain = Column(String(128), nullable=False, index=True)
    description = Column(Text, nullable=True)
    capabilities = Column(Text, nullable=True)
    tool_type = Column(String(64), nullable=False)  # sql_tool, api_tool, doc_tool, vector_tool, web_tool
    endpoint_or_schema = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    active = Column(Boolean, default=True, index=True)

    # Relationships
    quality = relationship("SourceQualityModel", back_populates="source", uselist=False, cascade="all, delete-orphan")
    embedding = relationship("SourceEmbeddingModel", back_populates="source", uselist=False, cascade="all, delete-orphan")
    logs = relationship("RetrievalLogModel", back_populates="source", cascade="all, delete-orphan")


class SourceQualityModel(Base):
    """
    Dynamic quality profile for source evaluation in AMORA.
    Tag: [C. AMORA Proposed Functionality - Source Profiling]
    """
    __tablename__ = "source_quality"

    source_id = Column(String(64), ForeignKey("source.source_id"), primary_key=True)
    reliability = Column(Float, default=1.0)
    freshness = Column(Float, default=1.0)
    cost = Column(Float, default=0.0)
    latency = Column(Float, default=0.1)
    availability = Column(Float, default=1.0)
    conflict_rate = Column(Float, default=0.0)
    historical_success = Column(Float, default=1.0)

    source = relationship("SourceModel", back_populates="quality")


class SourceEmbeddingModel(Base):
    """
    Dense metadata vector embedding storage for FAISS/Vector pre-filtering.
    Tag: [C. AMORA Proposed Functionality - Scalable Pre-filtering]
    """
    __tablename__ = "source_embedding"

    source_id = Column(String(64), ForeignKey("source.source_id"), primary_key=True)
    embedding_json = Column(Text, nullable=False)  # Store serialized json float list for universal SQL compatibility
    # Identity of the encoder that produced `embedding_json`. Vectors from different encoders
    # are not comparable, so the FAISS index only ingests rows matching the active signature.
    encoder_signature = Column(String(128), nullable=True, index=True)
    # Exact text that was embedded, so the vector can be recomputed if the encoder changes.
    embedding_text = Column(Text, nullable=True)

    source = relationship("SourceModel", back_populates="embedding")

    @property
    def embedding(self):
        return json.loads(self.embedding_json)

    @embedding.setter
    def embedding(self, value: list):
        self.embedding_json = json.dumps(value)


class RetrievalLogModel(Base):
    """
    Execution performance log for feedback loop & historical success tracking.
    Tag: [A. Logging & Monitoring]
    """
    __tablename__ = "retrieval_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(String(64), index=True, nullable=False)
    source_id = Column(String(64), ForeignKey("source.source_id"), nullable=False)
    tool = Column(String(64), nullable=False)
    retrieval_success = Column(Boolean, default=True)
    retrieval_latency = Column(Float, default=0.0)
    retrieved_documents = Column(Integer, default=0)
    answer_score = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    source = relationship("SourceModel", back_populates="logs")
