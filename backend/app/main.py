import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .core.config import PROJECT_NAME, VERSION, DESCRIPTION, SAMPLE_REPOS_DIR, WORKSPACE_DIR
from .models.schemas import ScanRequest, AuditReport, ApplyPatchRequest
from .db.database import init_db, get_report, list_scans
from .agent.orchestrator import AuditOrchestrator
from .agent.patch_generator import PatchGenerator
from .agent.reporter import Reporter

FRONTEND_DIST = WORKSPACE_DIR / "frontend" / "dist"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def classify_text(text: str) -> dict:
    text_lower = text.lower()
    category = "general"
    for label, words in (
        ("billing", ("refund", "invoice", "payment", "charge")),
        ("technical", ("error", "crash", "bug", "broken")),
        ("account", ("login", "password", "account", "sign in")),
    ):
        if any(word in text_lower for word in words):
            category = label
            break
    urgency = "high" if any(w in text_lower for w in ("urgent", "outage", "immediately")) else "low"
    return {"category": category, "urgency": urgency, "confidence": 0.85}

@app.get("/health")
async def root_health_check():
    return {"ok": True, "status": "ok", "app": PROJECT_NAME, "version": VERSION}

@app.post("/classify")
async def classify_endpoint(data: dict):
    text = data.get("text") if isinstance(data, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail="text_required")
    return classify_text(text)

@app.get("/api/health")
async def health_check():
    return {"ok": True, "status": "ok", "app": PROJECT_NAME, "version": VERSION}

@app.get("/api/samples")
async def get_sample_repositories():
    samples = []
    if SAMPLE_REPOS_DIR.exists():
        for d in SAMPLE_REPOS_DIR.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                readme_p = d / "README.md"
                desc = "Benchmark test repository"
                if readme_p.exists():
                    lines = readme_p.read_text(encoding="utf-8", errors="ignore").splitlines()
                    for l in lines:
                        if l.strip() and not l.startswith("#"):
                            desc = l.strip()
                            break
                samples.append({
                    "id": d.name,
                    "name": d.name.replace("-", " ").title(),
                    "path": str(d.resolve()),
                    "description": desc
                })
    return samples

@app.post("/api/scan/stream")
async def scan_repository_stream(request: ScanRequest):
    orchestrator = AuditOrchestrator(request)
    return StreamingResponse(
        orchestrator.stream_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/scan")
async def scan_repository_sync(request: ScanRequest):
    orchestrator = AuditOrchestrator(request)
    report = await orchestrator.execute_scan()
    return report

@app.get("/api/scan/{scan_id}")
async def get_scan_result(scan_id: str):
    report = await get_report(scan_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Audit scan '{scan_id}' not found")
    return report

@app.get("/api/history")
async def get_scan_history():
    return await list_scans()

@app.post("/api/patch/apply")
async def apply_diff_patch(req: ApplyPatchRequest):
    repo_path = None
    if req.scan_id:
        report = await get_report(req.scan_id)
        if report:
            repo_path = Path(report.metadata.repo_path)

    if not repo_path:
        repo_path = Path(req.file_path).resolve().parent

    success = PatchGenerator.apply_patch(repo_path, req.file_path, req.diff_patch)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to apply diff patch to target file")
    return {"status": "success", "message": f"Patch applied to {req.file_path}"}

@app.get("/api/export/{scan_id}")
async def export_audit_report(scan_id: str, format: str = "markdown"):
    report = await get_report(scan_id)
    if not report:
        raise HTTPException(status_code=404, detail="Scan not found")

    if format == "json":
        return Response(content=Reporter.to_json(report), media_type="application/json")
    elif format == "html":
        return Response(content=Reporter.to_html(report), media_type="text/html")
    else:
        return Response(content=Reporter.to_markdown(report), media_type="text/markdown")

# Mount built frontend static files if present
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
