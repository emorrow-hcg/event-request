"""Claude-powered resume optimizer and ATS scorer."""
import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"


def extract_job_requirements(job_text: str) -> dict:
    prompt = f"""Analyze this job description and extract structured information.
Return ONLY valid JSON with this exact shape:
{{
  "title": "Job title",
  "company": "Company name or empty string",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1", "skill2"],
  "required_qualifications": ["qual1", "qual2"],
  "preferred_qualifications": ["qual1", "qual2"],
  "keywords": ["keyword1", "keyword2"],
  "responsibilities": ["resp1", "resp2"],
  "experience_years": "e.g. 3-5 years or empty string"
}}

Job Description:
{job_text[:8000]}
"""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    # Strip markdown fences if present
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


def score_resume(resume_text: str, job_requirements: dict) -> dict:
    prompt = f"""You are an ATS (Applicant Tracking System) scoring engine.
Score this resume against the job requirements and return ONLY valid JSON:
{{
  "overall_score": 0-100,
  "keyword_score": 0-100,
  "skills_score": 0-100,
  "experience_score": 0-100,
  "education_score": 0-100,
  "matched_keywords": ["kw1", "kw2"],
  "missing_keywords": ["kw1", "kw2"],
  "matched_skills": ["s1", "s2"],
  "missing_skills": ["s1", "s2"],
  "strengths": ["strength1"],
  "gaps": ["gap1"]
}}

Job Requirements:
{json.dumps(job_requirements, indent=2)}

Resume:
{resume_text[:6000]}
"""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


def optimize_resume(resume_text: str, job_requirements: dict, score_data: dict) -> str:
    prompt = f"""You are an expert resume writer and ATS optimization specialist.

Rewrite and optimize the resume below to maximize its ATS score for the given job.
Rules:
- Keep all factual information accurate — do NOT invent experience or credentials
- Naturally incorporate missing keywords and skills where they genuinely apply
- Use strong action verbs and quantify achievements where possible
- Mirror language from the job description
- Format as clean plain text with standard resume sections
- Prioritize the most relevant experience for this role

Job Requirements:
{json.dumps(job_requirements, indent=2)}

ATS Gap Analysis:
- Missing keywords: {score_data.get('missing_keywords', [])}
- Missing skills: {score_data.get('missing_skills', [])}
- Gaps: {score_data.get('gaps', [])}

Original Resume:
{resume_text[:6000]}

Return the optimized resume text only — no commentary before or after.
"""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def build_resume_from_prompts(profile: dict, job_requirements: dict) -> str:
    prompt = f"""You are an expert resume writer. Build a professional, ATS-optimized resume
from the candidate profile below, tailored to the job requirements.

Rules:
- Use strong action verbs; quantify achievements where hints are given
- Incorporate relevant keywords naturally
- Format as clean plain text with standard sections:
  CONTACT | SUMMARY | SKILLS | EXPERIENCE | EDUCATION | CERTIFICATIONS (if any)
- Do not fabricate information not present in the profile

Job Requirements:
{json.dumps(job_requirements, indent=2)}

Candidate Profile:
{json.dumps(profile, indent=2)}

Return the resume text only.
"""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
