"""
Automatic REST API Metadata Profiler
Component Tag: [A. Offline Metadata Generation]
"""

from typing import Dict, Any
import requests
import json

class APIProfiler:
    """
    Parses OpenAPI/Swagger specs or REST API metadata.
    Tag: [A. Offline Metadata Generation]
    """

    @staticmethod
    def profile_openapi_spec(spec_source: str) -> Dict[str, Any]:
        """
        Extract endpoints, HTTP methods, parameters, and response descriptions.
        """
        try:
            if spec_source.startswith("http://") or spec_source.startswith("https://"):
                res = requests.get(spec_source, timeout=5)
                spec = res.json()
            elif isinstance(spec_source, str) and spec_source.strip().startswith("{"):
                spec = json.loads(spec_source)
            else:
                spec = {"paths": {}}

            endpoints = []
            paths = spec.get("paths", {})
            for path, methods in paths.items():
                for method, details in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE"]:
                        summary = details.get("summary", details.get("description", ""))
                        endpoints.append(f"{method.upper()} {path}: {summary}")

            endpoint_summary = " | ".join(endpoints) if endpoints else "REST API endpoints available"
            capabilities = "Real-time external REST API integration, HTTP GET/POST queries"

            return {
                "endpoint_summary": endpoint_summary,
                "capabilities": capabilities,
                "endpoint_count": len(endpoints)
            }
        except Exception as e:
            return {
                "endpoint_summary": f"API Profiler (Fallback): {str(e)}",
                "capabilities": "HTTP REST API",
                "endpoint_count": 0
            }
