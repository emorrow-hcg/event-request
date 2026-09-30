# Standard Operating Procedure — ATS Resume Optimizer

## Purpose

This SOP defines how to set up, run, develop, and maintain the ATS Resume Optimizer application — an AI-powered tool that parses job descriptions, scores resumes against ATS criteria, and generates optimized resume drafts using Claude AI.

---

## 1. Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | 3.11 recommended |
| pip | latest | `pip install --upgrade pip` |
| Node.js | 20+ | Only needed for JS linting in CI |
| Anthropic API Key | — | Obtain at console.anthropic.com |
| Git | 2.x+ | — |

---

## 2. Initial Setup

### 2.1 Clone the repository

```bash
git clone https://github.com/emorrow-hcg/event-request.git
cd event-request
```

### 2.2 Configure the API key

```bash
cp .env.example .env
# Edit .env and set your key:
# ANTHROPIC_API_KEY=sk-ant-...
```

### 2.3 Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## 3. Running the Application

### 3.1 One-command start (recommended)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
./start.sh
```

The app will be available at **http://localhost:8000**.

### 3.2 Manual start (development with auto-reload)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3.3 Verify the app is running

```bash
curl http://localhost:8000/
# Should return the frontend HTML
```

---

## 4. Using the Application

### Step 1 — Load a Job Description

Choose **one** of three input methods:

| Method | How |
|---|---|
| **URL** | Paste a direct link to a job posting (LinkedIn, Indeed, company site) |
| **File Upload** | Upload a `.pdf`, `.docx`, or `.txt` file of the job description |
| **Paste Text** | Copy/paste the job description text directly |

Click **Fetch & Analyze** or **Analyze**. The system will extract:
- Job title and company
- Required and preferred skills
- Required and preferred qualifications
- ATS keywords and responsibilities

### Step 2 — Input Your Resume / Experience

Choose **one** of three input methods:

| Method | When to use |
|---|---|
| **Upload Resume** | You have an existing resume as PDF, DOCX, or TXT |
| **Paste Resume** | You want to paste resume text directly |
| **Build from Scratch** | You don't have a resume — fill in the guided form |

Click **Optimize Resume** or **Build & Optimize Resume**.

> **Note:** Optimization takes 20–60 seconds. The AI rewrites your resume to match the job requirements without fabricating any experience or credentials.

### Step 3 — Review Results

| Panel | Contents |
|---|---|
| **Score view** | Before/after ATS score (0–100) with breakdown by keyword, skills, experience, education |
| **Optimized Resume** | Full rewritten resume text — copy or download as `.txt` |
| **Gap Analysis** | Matched vs. missing keywords and skills; strengths and gaps |

---

## 5. Development Workflow

### 5.1 Branch strategy

```
main            — stable, production-ready
feature/<name>  — one branch per feature or fix
```

All changes go through a pull request into `main`. No direct commits to `main`.

### 5.2 Making a change

```bash
git checkout main && git pull origin main
git checkout -b feature/my-change
# make edits
git add <files>
git commit -m "Brief description of what and why"
git push -u origin feature/my-change
# open a PR on GitHub
```

### 5.3 Running tests locally

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### 5.4 Running the linter locally

```bash
pip install ruff
ruff check backend/
```

Fix any issues before pushing — CI will block the PR otherwise.

---

## 6. CI Pipeline

Every push and pull request triggers three GitHub Actions jobs:

| Job | What it checks |
|---|---|
| **Lint & Validate** | Ruff linting, Python syntax check, backend import check |
| **Frontend Validate** | Presence of HTML/CSS/JS files, HTML parse check, JS syntax check |
| **Unit Tests** | Runs `pytest backend/tests/` with mocked Claude calls |

All three jobs must pass before a PR can be merged.

### 6.1 Interpreting CI failures

| Failure type | Where to look | Common fix |
|---|---|---|
| Ruff lint error | CI log `ruff check` output | Run `ruff check backend/ --fix` locally |
| Import error | CI log `Verify backend imports` | Check `requirements.txt` is up to date |
| Test failure | CI log `Run tests` | Fix the underlying logic or update mocks |
| JS syntax error | CI log `Run Node syntax check` | Open browser console locally to debug |

---

## 7. Project Structure

```
event-request/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI pipeline
├── backend/
│   ├── main.py             # FastAPI application and route handlers
│   ├── optimizer.py        # Claude API: job extraction, ATS scoring, resume rewriting
│   ├── parser.py           # Document parsing: URL, PDF, DOCX, plain text
│   ├── requirements.txt    # Python dependencies
│   └── tests/
│       ├── test_parser.py  # Unit tests for parser module
│       └── test_api.py     # Integration tests for API endpoints
├── frontend/
│   ├── index.html          # Single-page application markup
│   ├── style.css           # Dark-mode styles
│   └── app.js              # Tab workflow, API calls, result rendering
├── .env.example            # API key template
├── start.sh                # One-command startup script
└── SOP.md                  # This document
```

---

## 8. API Reference

All endpoints accept and return JSON (or multipart form data for file uploads).

### Job Description Endpoints

| Method | Path | Input | Output |
|---|---|---|---|
| `POST` | `/api/job/url` | `form: url` | `{raw_text, requirements}` |
| `POST` | `/api/job/file` | `multipart: file` | `{raw_text, requirements}` |
| `POST` | `/api/job/text` | `form: text` | `{raw_text, requirements}` |

### Resume Endpoints

| Method | Path | Input | Output |
|---|---|---|---|
| `POST` | `/api/resume/optimize` | `json: {resume_text, job_requirements}` | `{original_score, optimized_resume, optimized_score}` |
| `POST` | `/api/resume/file` | `multipart: file + form: requirements (JSON)` | `{original_resume, original_score, optimized_resume, optimized_score}` |
| `POST` | `/api/resume/build` | `json: {profile, job_requirements}` | `{resume, score}` |

### Score object shape

```json
{
  "overall_score": 85,
  "keyword_score": 88,
  "skills_score": 80,
  "experience_score": 82,
  "education_score": 90,
  "matched_keywords": ["Python", "REST API"],
  "missing_keywords": ["Kubernetes"],
  "matched_skills": ["Python", "SQL"],
  "missing_skills": ["Docker"],
  "strengths": ["Strong Python background"],
  "gaps": ["No cloud experience mentioned"]
}
```

---

## 9. Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `ANTHROPIC_API_KEY not configured` | Env var not set | `export ANTHROPIC_API_KEY=sk-ant-...` |
| `Could not fetch URL` | Site blocks scrapers | Download the page as a file and use file upload instead |
| Optimization takes >90s | Claude API slowness | Wait — it's normal during peak API load |
| Score stays the same after optimization | Resume already well-matched | Review the Gap Analysis panel for remaining items |
| `422 Unprocessable Entity` | Malformed request body | Check that `job_requirements` is valid JSON |
| PDF returns empty text | Scanned/image-based PDF | Convert to text using OCR first, then paste |

---

## 10. Security Notes

- The `ANTHROPIC_API_KEY` must **never** be committed to the repository. It is listed in `.gitignore` via `.env`.
- The app currently has no authentication. For production deployment, add an auth layer (e.g. API key header, OAuth) before exposing it publicly.
- Uploaded files are processed in-memory and never written to disk.
- Resume and job description text is sent to the Anthropic API. Do not submit confidential or regulated data (SSNs, medical records) through the tool.
