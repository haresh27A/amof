"""
AMORA RAG System - FastAPI Main Application
Component Tag: [A. Core Server Entrypoint]
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
import uvicorn

from backend.config import settings
from database.session import init_db, SessionLocal
from datasets.demo_data import populate_demo_sources
from backend.api import sources, query, evaluation

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Flutter is the only UI. The FastAPI server optionally hosts its web build so the app is
# reachable in a browser at /app; native builds run the same Dart code on device.
FLUTTER_WEB_DIR = os.path.abspath(
    os.getenv(
        "FLUTTER_WEB_DIR",
        os.path.join(BASE_DIR, "frontend", "flutter_app", "build", "web")
    )
)

_NO_BUILD_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>AMORA — UI not built</title>
<style>body{font-family:system-ui,sans-serif;max-width:44rem;margin:4rem auto;padding:0 1.5rem;
line-height:1.6;color:#1a1a1a}code{background:#f4f4f5;padding:.15rem .4rem;border-radius:4px}
pre{background:#f4f4f5;padding:1rem;border-radius:6px;overflow-x:auto}</style></head>
<body>
<h1>Flutter web build not found</h1>
<p>The API is running, but no compiled Flutter web bundle is present, so there is no UI to
serve at this URL.</p>
<p>Build it from the Flutter project:</p>
<pre>cd frontend/flutter_app
flutter pub get
flutter build web</pre>
<p>Then reload this page. The API is available in the meantime at
<a href="/docs">/docs</a>.</p>
</body></html>"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB schema and seed demo sources on startup."""
    init_db()
    db = SessionLocal()
    try:
        populate_demo_sources(db)
    except Exception as e:
        print(f"Startup demo seed note: {e}")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Adaptive Multi-Objective Reasoning Algorithm for External Source Routing and Tool Coordination in LLM-based RAG",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for the Flutter clients (web, desktop, mobile).
# The Flutter web build is served same-origin from this app, so CORS only matters for
# native builds running against a remote host.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router modules
app.include_router(query.router)
app.include_router(sources.router)
app.include_router(evaluation.router)

def _resolve_web_asset(relative_path: str):
    """
    Resolve a path inside the Flutter web build, or None if it escapes the root
    or does not exist.
    """
    if not relative_path:
        return None
    candidate = os.path.normpath(os.path.join(FLUTTER_WEB_DIR, relative_path))
    # Reject traversal outside the build directory.
    if os.path.commonpath([candidate, FLUTTER_WEB_DIR]) != FLUTTER_WEB_DIR:
        return None
    return candidate if os.path.isfile(candidate) else None


@app.get("/", response_model=None)
def root(request: Request):
    """
    Root endpoint: Serves the Flutter web app to browsers, or returns status JSON to API clients.
    """
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/app/", status_code=307)

    return {
        "status": "online",
        "app_name": settings.app_name,
        "web_app_url": "/app/",
        "docs_url": "/docs",
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.embedding_model,
        "flutter_web_build_present": os.path.isfile(
            os.path.join(FLUTTER_WEB_DIR, "index.html")
        ),
    }


@app.get("/app", response_model=None)
def app_redirect():
    """Ensure trailing slash so relative paths in HTML resolve correctly."""
    return RedirectResponse(url="/app/", status_code=307)


@app.get("/app/", response_model=None)
@app.get("/app/{web_path:path}", response_model=None)
def serve_app(web_path: str = ""):
    """
    Serves the compiled Flutter web bundle.

    Falls back to index.html for unknown paths so client-side routes survive a page
    reload (Flutter web uses path-based URLs by default).
    """
    resolved = _resolve_web_asset(web_path)
    if resolved:
        return FileResponse(resolved)

    index = _resolve_web_asset("index.html")
    if not index:
        return HTMLResponse(_NO_BUILD_HTML, status_code=503)
    return FileResponse(index)


@app.get("/{root_asset:path}", response_model=None)
def serve_root_asset(root_asset: str):
    """
    Fallback for any assets requested directly at root level.
    """
    resolved = _resolve_web_asset(root_asset)
    if resolved:
        return FileResponse(resolved)
    raise HTTPException(status_code=404, detail="Not Found")


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=settings.debug)


