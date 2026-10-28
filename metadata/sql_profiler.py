"""
Automatic SQL Metadata Profiler
Component Tag: [A. Offline Metadata Generation]
"""

from typing import Dict, Any
from sqlalchemy import create_engine, inspect

class SQLProfiler:
    """
    Extracts structural metadata from SQL databases using SQLAlchemy Inspector.
    Tag: [A. Offline Metadata Generation]
    """

    @staticmethod
    def profile_database(connection_string: str) -> Dict[str, Any]:
        """
        Inspect SQL database schemas, tables, columns, and data types.
        """
        try:
            engine = create_engine(connection_string)
            inspector = inspect(engine)
            
            tables_summary = []
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                col_descriptors = [f"{c['name']} ({c['type']})" for c in columns]
                tables_summary.append(f"Table '{table_name}': {', '.join(col_descriptors)}")

            schema_summary = " | ".join(tables_summary)
            capabilities = "Structured relational queries, aggregations, joins, historical transactions"

            return {
                "schema_summary": schema_summary,
                "capabilities": capabilities,
                "table_count": len(tables_summary)
            }
        except Exception as e:
            return {
                "schema_summary": f"SQL Schema Inspection (Fallback): {str(e)}",
                "capabilities": "Structured database queries",
                "table_count": 0
            }
