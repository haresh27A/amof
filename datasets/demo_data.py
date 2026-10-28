"""
AMORA Demo Environment & Ground Truth Dataset Initialization
Component Tag: [A. Dataset & Demo Setup]
"""

import os
import json
import sqlite3
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from database.session import SessionLocal, init_db
from metadata.generator import MetadataGenerator
from metadata.repository import MetadataRepository

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))

def create_demo_sqlite_database(db_path: str) -> str:
    """Create a realistic demo SQLite database with products, customers, orders, inventory tables."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            unit_price REAL,
            supplier TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            stock_quantity INTEGER,
            warehouse_location TEXT,
            last_restock_date TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            product_id TEXT,
            quantity INTEGER,
            total_amount REAL,
            order_date TEXT
        );
    """)

    # Populate sample rows if empty
    cur.execute("SELECT COUNT(*) FROM products;")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?);", [
            ("P-101", "Quantum X Laptop", "Electronics", 1299.99, "TechCorp"),
            ("P-102", "Aura Pro Wireless Headphones", "Audio", 199.99, "SoundMax"),
            ("P-103", "Ergonomic Lumbar Office Chair", "Furniture", 299.50, "ComfortDesign"),
            ("P-104", "UltraHD 4K Smart Monitor", "Electronics", 450.00, "DisplayVision")
        ])

        cur.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?);", [
            ("P-101", 45, "Warehouse A - Rack 12", "2026-08-01"),
            ("P-102", 120, "Warehouse B - Rack 04", "2026-08-05"),
            ("P-103", 18, "Warehouse A - Rack 08", "2026-07-20"),
            ("P-104", 60, "Warehouse C - Rack 02", "2026-08-07")
        ])

        cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?);", [
            ("ORD-9001", "Alice Smith", "P-101", 2, 2599.98, "2026-08-02"),
            ("ORD-9002", "Bob Jones", "P-102", 1, 199.99, "2026-08-03"),
            ("ORD-9003", "Carol White", "P-101", 5, 6499.95, "2026-08-06")
        ])

    conn.commit()
    conn.close()
    return db_path


def create_demo_policy_document(doc_path: str) -> str:
    """Create demo text file representing company policy document."""
    content = """
    COMPANY RETURN AND WARRANTY POLICY 2026
    
    1. Return Period:
       Customers may return any unopened merchandise within 30 calendar days from the delivery date for a full refund.
    
    2. Condition & Packaging:
       Items must be in original condition with intact serial tags and all original packaging accessories.
    
    3. Electronics Warranty:
       All Quantum X Laptops and Aura Pro Headphones include a 12-month manufacturer limited warranty covering hardware defects.
    
    4. Refund Processing Time:
       Approved refunds are processed to the original payment method within 5-7 business days upon receipt at Warehouse A.
    """
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    return doc_path


def get_direct_dataset_context(query: str = "") -> str:
    """
    Directly retrieves relevant enterprise dataset facts for a query WITHOUT needing AMORA routing.
    Enables baseline LLMs (Gemini, Qwen, etc.) to access enterprise policies, inventory, products, and sales.
    """
    q_lower = query.lower()
    facts = []

    # 1. Company Return & Warranty Policy
    if any(k in q_lower for k in ["return", "policy", "warranty", "refund", "unopened", "warehouse a", "headphone", "merchandise"]):
        doc_path = os.path.join(DEMO_DIR, "company_policy.txt")
        if os.path.exists(doc_path):
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    facts.append(f"[Source: Company Policy & Legal Documentation (company_policy.txt)]:\n{f.read().strip()}")
            except Exception:
                pass

    # 2. Products, Inventory & Sales Database
    if any(k in q_lower for k in ["quantum", "laptop", "inventory", "stock", "product", "sales", "revenue", "order", "price", "warehouse", "p-101", "p-102", "chair", "monitor"]):
        db_path = os.path.join(DEMO_DIR, "demo_sales.db")
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                rows = cur.execute("""
                    SELECT p.product_id, p.name, p.category, p.unit_price, p.supplier,
                           i.stock_quantity, i.warehouse_location, i.last_restock_date
                    FROM products p
                    LEFT JOIN inventory i ON p.product_id = i.product_id
                """).fetchall()
                prod_lines = [
                    f"- {r[1]} ({r[0]}): Category: {r[2]}, Price: ${r[3]:.2f}, In Stock: {r[5]} units at {r[6]} (Restocked: {r[7]}) [Supplier: {r[4]}]"
                    for r in rows
                ]
                facts.append("[Source: Enterprise Sales & Inventory Database - Products & Stock]:\n" + "\n".join(prod_lines))

                if any(k in q_lower for k in ["sale", "revenue", "highest", "order"]):
                    order_rows = cur.execute("""
                        SELECT p.name, SUM(o.quantity) as total_qty, SUM(o.total_amount) as total_rev
                        FROM orders o
                        JOIN products p ON o.product_id = p.product_id
                        GROUP BY p.name
                        ORDER BY total_rev DESC
                    """).fetchall()
                    order_lines = [
                        f"- {r[0]}: Total Units Sold: {r[1]}, Total Revenue: ${r[2]:.2f}"
                        for r in order_rows
                    ]
                    facts.append("[Source: Enterprise Sales & Inventory Database - Sales Revenue]:\n" + "\n".join(order_lines))
                conn.close()
            except Exception:
                pass

    # If general enterprise inquiry, provide concise overview
    if not facts and any(k in q_lower for k in ["company", "internal", "data", "catalog", "help"]):
        doc_path = os.path.join(DEMO_DIR, "company_policy.txt")
        if os.path.exists(doc_path):
            with open(doc_path, "r", encoding="utf-8") as f:
                facts.append(f"[Source: Company Policy & Legal Documentation]:\n{f.read().strip()[:200]}...")

    return "\n\n".join(facts)


def create_source_mapping_dataset(mapping_path: str):
    """Create source mapping ground truth dataset for evaluation queries."""
    mappings = [
        {
            "query_id": "q001",
            "query": "What is the current inventory stock quantity of Quantum X Laptop?",
            "gold_sources": ["src_demo_sql"],
            "acceptable_sources": ["src_demo_sql", "src_demo_api"],
            "domain": "inventory",
            "requires_retrieval": True,
            "required_tool": "sql_tool",
            "gold_answer": "45 units in Warehouse A."
        },
        {
            "query_id": "q002",
            "query": "What does the company return policy say about unopened merchandise and refund timeframe?",
            "gold_sources": ["src_demo_doc"],
            "acceptable_sources": ["src_demo_doc"],
            "domain": "legal_policy",
            "requires_retrieval": True,
            "required_tool": "doc_tool",
            "gold_answer": "Unopened merchandise can be returned within 30 days; refunds take 5-7 business days."
        },
        {
            "query_id": "q003",
            "query": "Which product has generated the highest sales revenue?",
            "gold_sources": ["src_demo_sql"],
            "acceptable_sources": ["src_demo_sql"],
            "domain": "sales",
            "requires_retrieval": True,
            "required_tool": "sql_tool",
            "gold_answer": "Quantum X Laptop (P-101) with $9,099.93 total sales."
        },
        {
            "query_id": "q004",
            "query": "What is the capital of France?",
            "gold_sources": [],
            "acceptable_sources": [],
            "domain": "general_knowledge",
            "requires_retrieval": False,
            "required_tool": None,
            "gold_answer": "Paris."
        }
    ]
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2)


def populate_demo_sources(db: Session):
    """Seed DB with initial demo sources."""
    init_db()
    repo = MetadataRepository(db)

    # 1. SQL Source
    sql_path = os.path.join(DEMO_DIR, "demo_sales.db")
    create_demo_sqlite_database(sql_path)
    sql_conn_str = f"sqlite:///{sql_path.replace('\\', '/')}"

    meta_sql = MetadataGenerator.generate_source_metadata(
        source_id="src_demo_sql",
        name="Enterprise Sales & Inventory Database",
        source_type="SQL Database",
        domain="sales_inventory",
        description="Relational database containing live tables for products, orders, customers, and warehouse inventory stock levels.",
        endpoint_or_schema=sql_conn_str,
        tool_type="sql_tool",
        reliability=0.98,
        cost=0.05,
        latency=0.10,
        availability=0.99
    )
    repo.register_source(meta_sql)

    # 2. PDF/Document Source
    doc_path = os.path.join(DEMO_DIR, "company_policy.txt")
    create_demo_policy_document(doc_path)
    meta_doc = MetadataGenerator.generate_source_metadata(
        source_id="src_demo_doc",
        name="Company Policy & Legal Documentation",
        source_type="PDF Document",
        domain="legal_policy",
        description="Official company document detailing customer return windows, warranty terms, and warehouse refund protocols.",
        endpoint_or_schema=doc_path,
        tool_type="doc_tool",
        reliability=0.95,
        cost=0.02,
        latency=0.12,
        availability=1.00
    )
    repo.register_source(meta_doc)

    # 3. REST API Source
    meta_api = MetadataGenerator.generate_source_metadata(
        source_id="src_demo_api",
        name="Product Specs & Pricing REST API",
        source_type="REST API",
        domain="product_specs",
        description="REST API service providing real-time product specification sheets, SKU lookup, and live unit prices.",
        endpoint_or_schema="https://api.demo-products.com/v1",
        tool_type="api_tool",
        reliability=0.92,
        cost=0.15,
        latency=0.25,
        availability=0.97
    )
    repo.register_source(meta_api)

    # 4. FAISS Vector Source
    meta_vector = MetadataGenerator.generate_source_metadata(
        source_id="src_demo_vector",
        name="Customer Support Vector Knowledge Store",
        source_type="Vector DB",
        domain="support_kb",
        description="Dense vector embeddings index for customer support FAQs, troubleshooting guides, and knowledge base articles.",
        endpoint_or_schema="faiss://customer_kb_index",
        tool_type="vector_tool",
        reliability=0.89,
        cost=0.08,
        latency=0.15,
        availability=0.98
    )
    repo.register_source(meta_vector)

    # 5. Populate 52 Production Enterprise Sources
    try:
        from datasets.enterprise_catalog import ENTERPRISE_SOURCES
        for src in ENTERPRISE_SOURCES:
            meta_ent = MetadataGenerator.generate_source_metadata(
                source_id=src["source_id"],
                name=src["name"],
                source_type=src["source_type"],
                domain=src["domain"],
                description=src["description"],
                endpoint_or_schema=src["endpoint_or_schema"],
                tool_type=src.get("tool_type"),
                reliability=src.get("reliability", 0.95),
                cost=src.get("cost", 0.05),
                latency=src.get("latency", 0.10),
                availability=src.get("availability", 0.99)
            )
            repo.register_source(meta_ent)
        print(f"Registered {len(ENTERPRISE_SOURCES)} enterprise sources into repository.")
    except Exception as e:
        print(f"Note loading enterprise sources: {e}")

    # Save mapping file
    mapping_path = os.path.join(DEMO_DIR, "source_mapping.json")
    create_source_mapping_dataset(mapping_path)


if __name__ == "__main__":
    db = SessionLocal()
    try:
        populate_demo_sources(db)
        print("Successfully populated demo sources and database!")
    finally:
        db.close()
