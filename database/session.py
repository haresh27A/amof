"""
Database Session Management
Component Tag: [A. Infrastructure]
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from database.models import Base

# Support SQLite or PostgreSQL
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_columns() -> None:
    """
    Additive, idempotent schema migrations.

    Base.metadata.create_all() only creates missing tables — it never adds columns to
    existing ones, so newly introduced columns are applied here. Safe to run repeatedly.
    """
    additions = {
        "source_embedding": [
            ("encoder_signature", "VARCHAR(128)"),
            ("embedding_text", "TEXT"),
        ],
    }

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table, columns in additions.items():
            if table not in existing_tables:
                continue
            present = {col["name"] for col in inspector.get_columns(table)}
            for col_name, col_type in columns:
                if col_name in present:
                    continue
                conn.execute(
                    text(f'ALTER TABLE "{table}" ADD COLUMN "{col_name}" {col_type}')
                )

        # Index for the encoder-signature lookup (SQLite cannot add an index in the same
        # statement as the column, so it is issued separately).
        if "source_embedding" in existing_tables:
            conn.execute(
                text(
                    'CREATE INDEX IF NOT EXISTS ix_source_embedding_encoder_signature '
                    'ON "source_embedding" (encoder_signature)'
                )
            )


def init_db():
    """Initialize tables and apply additive schema migrations."""
    Base.metadata.create_all(bind=engine)
    _ensure_columns()

def get_db():
    """FastAPI dependency yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
