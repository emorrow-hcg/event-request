"""Integration tests for FastAPI endpoints (no real Claude calls)."""
import sys
import os
import pytest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

MOCK_REQUIREMENTS = {
    "title": "Software Engineer",
    "company": "Acme Corp",
    "required_skills": ["Python", "SQL"],
    "preferred_skills": ["Docker"],
    "required_qualifications": ["Bachelor's degree"],
    "preferred_qualifications": ["Master's degree"],
    "keywords": ["Python", "REST API"],
    "responsibilities": ["Build APIs"],
    "experience_years": "3-5 years",
}

MOCK_SCORE = {
    "overall_score": 82,
    "keyword_score": 85,
    "skills_score": 80,
    "experience_score": 78,
    "education_score": 90,
    "matched_keywords": ["Python"],
    "missing_keywords": ["REST API"],
    "matched_skills": ["Python"],
    "missing_skills": ["SQL"],
    "strengths": ["Strong Python background"],
    "gaps": ["No SQL mentioned"],
}


@pytest.fixture(autouse=True)
def mock_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")


@patch("optimizer.extract_job_requirements", return_value=MOCK_REQUIREMENTS)
def test_job_from_text(mock_extract):
    resp = client.post("/api/job/text", data={"text": "We are hiring a Software Engineer with Python skills."})
    assert resp.status_code == 200
    body = resp.json()
    assert "requirements" in body
    assert body["requirements"]["title"] == "Software Engineer"


@patch("optimizer.score_resume", return_value=MOCK_SCORE)
@patch("optimizer.optimize_resume", return_value="Optimized resume text here.")
def test_optimize_resume(mock_opt, mock_score):
    payload = {
        "resume_text": "John Doe\nPython developer with 4 years experience.",
        "job_requirements": MOCK_REQUIREMENTS,
    }
    resp = client.post("/api/resume/optimize", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "optimized_resume" in body
    assert "original_score" in body
    assert "optimized_score" in body


@patch("optimizer.score_resume", return_value=MOCK_SCORE)
@patch("optimizer.build_resume_from_prompts", return_value="Built resume text here.")
def test_build_resume(mock_build, mock_score):
    payload = {
        "profile": {"name": "Jane Smith", "skills": "Python, SQL"},
        "job_requirements": MOCK_REQUIREMENTS,
    }
    resp = client.post("/api/resume/build", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "resume" in body
    assert "score" in body


def test_missing_api_key_returns_500(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    resp = client.post("/api/job/text", data={"text": "some job"})
    assert resp.status_code == 500
