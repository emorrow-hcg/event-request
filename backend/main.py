"""ATS Resume Optimizer — FastAPI backend."""
import os
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import parser as doc_parser
import optimizer

app = FastAPI(title="ATS Resume Optimizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── helpers ──────────────────────────────────────────────────────────────────

def _require_api_key():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")


# ── job description endpoints ─────────────────────────────────────────────────

@app.post("/api/job/url")
async def job_from_url(url: str = Form(...)):
    _require_api_key()
    try:
        text = doc_parser.parse_url(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")
    requirements = optimizer.extract_job_requirements(text)
    return {"raw_text": text[:3000], "requirements": requirements}


@app.post("/api/job/file")
async def job_from_file(file: UploadFile = File(...)):
    _require_api_key()
    data = await file.read()
    name = file.filename or ""
    if name.endswith(".pdf"):
        text = doc_parser.parse_pdf(data)
    elif name.endswith(".docx"):
        text = doc_parser.parse_docx(data)
    else:
        text = doc_parser.parse_text(data.decode("utf-8", errors="replace"))
    requirements = optimizer.extract_job_requirements(text)
    return {"raw_text": text[:3000], "requirements": requirements}


@app.post("/api/job/text")
async def job_from_text(text: str = Form(...)):
    _require_api_key()
    cleaned = doc_parser.parse_text(text)
    requirements = optimizer.extract_job_requirements(cleaned)
    return {"raw_text": cleaned[:3000], "requirements": requirements}


# ── resume optimization endpoints ─────────────────────────────────────────────

class OptimizeRequest(BaseModel):
    resume_text: str
    job_requirements: dict


@app.post("/api/resume/optimize")
async def optimize_resume(req: OptimizeRequest):
    _require_api_key()
    score = optimizer.score_resume(req.resume_text, req.job_requirements)
    optimized = optimizer.optimize_resume(req.resume_text, req.job_requirements, score)
    new_score = optimizer.score_resume(optimized, req.job_requirements)
    return {
        "original_score": score,
        "optimized_resume": optimized,
        "optimized_score": new_score,
    }


@app.post("/api/resume/file")
async def resume_from_file(
    file: UploadFile = File(...),
    requirements: str = Form(...),
):
    _require_api_key()
    import json
    job_req = json.loads(requirements)
    data = await file.read()
    name = file.filename or ""
    if name.endswith(".pdf"):
        resume_text = doc_parser.parse_pdf(data)
    elif name.endswith(".docx"):
        resume_text = doc_parser.parse_docx(data)
    else:
        resume_text = doc_parser.parse_text(data.decode("utf-8", errors="replace"))

    score = optimizer.score_resume(resume_text, job_req)
    optimized = optimizer.optimize_resume(resume_text, job_req, score)
    new_score = optimizer.score_resume(optimized, job_req)
    return {
        "original_resume": resume_text,
        "original_score": score,
        "optimized_resume": optimized,
        "optimized_score": new_score,
    }


class BuildRequest(BaseModel):
    profile: dict
    job_requirements: dict


@app.post("/api/resume/build")
async def build_resume(req: BuildRequest):
    _require_api_key()
    resume_text = optimizer.build_resume_from_prompts(req.profile, req.job_requirements)
    score = optimizer.score_resume(resume_text, req.job_requirements)
    return {"resume": resume_text, "score": score}


# ── serve frontend ────────────────────────────────────────────────────────────

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
