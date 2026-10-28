"""
Synthetic Enterprise Source Catalog Generator (10,000 Sources)
Component Tag: [A. Dataset Infrastructure]

Generates realistic synthetic source metadata catalog for AMORA scalability experiments.
"""

import json
import random
import os
import pandas as pd
from typing import List, Dict, Any

SOURCE_TYPES = ["SQL", "REST API", "PDF Document", "Vector DB", "Web Source", "Knowledge Graph"]
TOOL_TYPES = {
    "SQL": "sql_tool",
    "REST API": "api_tool",
    "PDF Document": "doc_tool",
    "Vector DB": "vector_tool",
    "Web Source": "web_tool",
    "Knowledge Graph": "api_tool"
}

DOMAINS = ["E-commerce", "Finance", "Healthcare", "Legal", "Supply Chain", "HR", "Customer Support", "Research", "IT Operations"]

ADJECTIVES = ["Enterprise", "Global", "Internal", "Primary", "Legacy", "Real-Time", "Core", "Secure", "Analytical"]

def generate_catalog(count: int = 10000) -> List[Dict[str, Any]]:
    """
    Generate reproducible synthetic source metadata records for scalability experiments.
    """
    random.seed(42)
    sources = []

    for i in range(1, count + 1):
        s_type = random.choice(SOURCE_TYPES)
        domain = random.choice(DOMAINS)
        adj = random.choice(ADJECTIVES)
        tool_type = TOOL_TYPES[s_type]

        source_id = f"src_{i:05d}"
        name = f"{adj} {domain} {s_type} #{i}"
        description = f"{adj} source for {domain} operations containing domain-specific records and structural indexes."
        capabilities = f"Provides high-performance access to {domain} data using {tool_type} connector."

        reliability = round(random.uniform(0.60, 0.99), 4)
        freshness = round(random.uniform(0.50, 1.00), 4)
        cost = round(random.uniform(0.01, 0.40), 4)
        latency = round(random.uniform(0.05, 0.80), 4)
        availability = round(random.uniform(0.85, 1.00), 4)
        historical_success = round(random.uniform(0.70, 0.99), 4)
        conflict_rate = round(random.uniform(0.00, 0.15), 4)

        record = {
            "source_id": source_id,
            "name": name,
            "domain": domain.lower().replace(" ", "_"),
            "description": description,
            "capabilities": capabilities,
            "source_type": s_type,
            "tool_type": tool_type,
            "endpoint_or_schema": f"synthetic://{domain.lower()}/{source_id}",
            "reliability": reliability,
            "freshness": freshness,
            "cost": cost,
            "latency": latency,
            "availability": availability,
            "historical_success": historical_success,
            "conflict_rate": conflict_rate
        }
        sources.append(record)

    return sources

def save_synthetic_dataset(output_dir: str, count: int = 10000):
    os.makedirs(output_dir, exist_ok=True)
    catalog = generate_catalog(count)
    
    # Save CSV
    df = pd.DataFrame(catalog)
    csv_path = os.path.join(output_dir, "source_metadata.csv")
    df.to_csv(csv_path, index=False)

    # Save JSON
    json_path = os.path.join(output_dir, "synthetic_catalog_10k.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    print(f"Generated {count} synthetic source metadata records in {output_dir}")

if __name__ == "__main__":
    out = os.path.dirname(os.path.abspath(__file__))
    save_synthetic_dataset(out, 10000)
