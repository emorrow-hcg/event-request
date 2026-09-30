const API = "";  // same origin
let jobRequirements = null;
let optimizedResumeText = "";

// ── Tab switching ─────────────────────────────────────────────────────────────
document.querySelectorAll(".tab-bar").forEach(bar => {
  bar.addEventListener("click", e => {
    const btn = e.target.closest(".tab");
    if (!btn) return;
    const tabId = btn.dataset.tab;
    const card = bar.closest(".card, section");
    bar.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");
    card.querySelectorAll(".tab-panel").forEach(p => {
      p.classList.toggle("active", p.id === "tab-" + tabId);
    });
  });
});

document.querySelectorAll(".result-tabs").forEach(bar => {
  bar.addEventListener("click", e => {
    const btn = e.target.closest(".tab");
    if (!btn) return;
    const tabId = btn.dataset.resultTab;
    bar.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");
    document.querySelectorAll(".result-panel").forEach(p => {
      p.classList.toggle("active", p.id === "result-" + tabId);
    });
  });
});

// ── Status helpers ────────────────────────────────────────────────────────────
function setStatus(id, type, msg) {
  const el = document.getElementById(id);
  el.className = "status " + type;
  el.textContent = msg;
}

// ── Job Description ───────────────────────────────────────────────────────────
async function loadJobFromUrl() {
  const url = document.getElementById("job-url").value.trim();
  if (!url) return alert("Enter a URL first.");
  setStatus("job-status", "loading", "Fetching job posting…");
  const fd = new FormData();
  fd.append("url", url);
  await _loadJob("/api/job/url", fd);
}

async function loadJobFromFile() {
  const file = document.getElementById("job-file").files[0];
  if (!file) return;
  setStatus("job-status", "loading", `Parsing ${file.name}…`);
  const fd = new FormData();
  fd.append("file", file);
  await _loadJob("/api/job/file", fd);
}

async function loadJobFromText() {
  const text = document.getElementById("job-text").value.trim();
  if (!text) return alert("Paste job description text first.");
  setStatus("job-status", "loading", "Analyzing job description…");
  const fd = new FormData();
  fd.append("text", text);
  await _loadJob("/api/job/text", fd);
}

async function _loadJob(endpoint, formData) {
  try {
    const res = await fetch(API + endpoint, { method: "POST", body: formData });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    const data = await res.json();
    jobRequirements = data.requirements;
    renderRequirements(data.requirements);
    setStatus("job-status", "success", "Job requirements extracted successfully.");
    show("requirements-section");
    show("step2");
  } catch (err) {
    setStatus("job-status", "error", "Error: " + err.message);
  }
}

function renderRequirements(req) {
  const el = document.getElementById("requirements-display");
  el.innerHTML = `
    <div style="margin-bottom:12px">
      <strong style="font-size:18px">${req.title || "Position"}</strong>
      ${req.company ? `<span style="color:var(--text-muted)"> at ${req.company}</span>` : ""}
      ${req.experience_years ? `<span class="tag" style="margin-left:8px;font-size:12px">${req.experience_years}</span>` : ""}
    </div>
    <div class="req-grid">
      ${section("Required Skills", req.required_skills, "tag")}
      ${section("Preferred Skills", req.preferred_skills, "tag yellow")}
      ${section("Required Qualifications", req.required_qualifications, "tag")}
      ${section("Preferred Qualifications", req.preferred_qualifications, "tag yellow")}
      ${section("Key Keywords", req.keywords, "tag green")}
      ${section("Responsibilities", req.responsibilities, "tag")}
    </div>`;
}

function section(title, items, tagClass) {
  if (!items || !items.length) return "";
  return `<div class="req-group">
    <h3>${title}</h3>
    <div class="tag-list">${items.map(i => `<span class="${tagClass}">${i}</span>`).join("")}</div>
  </div>`;
}

// ── Resume file handling ──────────────────────────────────────────────────────
function handleResumeFile() {
  const file = document.getElementById("resume-file").files[0];
  if (!file) return;
  document.getElementById("resume-file-name").textContent = file.name;
  document.getElementById("optimize-file-btn").classList.remove("hidden");
}

async function optimizeResumeFile() {
  if (!jobRequirements) return alert("Load a job description first.");
  const file = document.getElementById("resume-file").files[0];
  if (!file) return;
  setStatus("resume-status", "loading", "Parsing and optimizing your resume… this may take 20-40s.");
  const fd = new FormData();
  fd.append("file", file);
  fd.append("requirements", JSON.stringify(jobRequirements));
  try {
    const res = await fetch(API + "/api/resume/file", { method: "POST", body: fd });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    const data = await res.json();
    renderResults(data.original_score, data.optimized_score, data.optimized_resume);
    setStatus("resume-status", "success", "Resume optimized!");
  } catch (err) {
    setStatus("resume-status", "error", "Error: " + err.message);
  }
}

async function optimizeResumeText() {
  if (!jobRequirements) return alert("Load a job description first.");
  const text = document.getElementById("resume-text-input").value.trim();
  if (!text) return alert("Paste your resume first.");
  setStatus("resume-status", "loading", "Optimizing your resume… this may take 20-40s.");
  try {
    const res = await fetch(API + "/api/resume/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: text, job_requirements: jobRequirements }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    const data = await res.json();
    renderResults(data.original_score, data.optimized_score, data.optimized_resume);
    setStatus("resume-status", "success", "Resume optimized!");
  } catch (err) {
    setStatus("resume-status", "error", "Error: " + err.message);
  }
}

// ── Build from scratch ────────────────────────────────────────────────────────
function addExpEntry() {
  const container = document.getElementById("exp-entries");
  const div = document.createElement("div");
  div.className = "exp-entry";
  div.innerHTML = `
    <input type="text" placeholder="Job Title" class="exp-title" />
    <input type="text" placeholder="Company" class="exp-company" />
    <input type="text" placeholder="Dates (e.g. Jan 2020 – Present)" class="exp-dates" />
    <textarea rows="3" placeholder="Key responsibilities and achievements…" class="exp-desc"></textarea>`;
  container.appendChild(div);
}

async function buildFromScratch() {
  if (!jobRequirements) return alert("Load a job description first.");
  const profile = {
    name: document.getElementById("b-name").value,
    contact: document.getElementById("b-contact").value,
    links: document.getElementById("b-links").value,
    summary: document.getElementById("b-summary").value,
    skills: document.getElementById("b-skills").value,
    education: document.getElementById("b-edu").value,
    certifications: document.getElementById("b-certs").value,
    experience: [...document.querySelectorAll(".exp-entry")].map(e => ({
      title: e.querySelector(".exp-title").value,
      company: e.querySelector(".exp-company").value,
      dates: e.querySelector(".exp-dates").value,
      description: e.querySelector(".exp-desc").value,
    })).filter(e => e.title || e.company),
  };
  setStatus("resume-status", "loading", "Building and optimizing your resume… this may take 30-60s.");
  try {
    const res = await fetch(API + "/api/resume/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile, job_requirements: jobRequirements }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    const data = await res.json();
    renderResults(null, data.score, data.resume);
    setStatus("resume-status", "success", "Resume built and optimized!");
  } catch (err) {
    setStatus("resume-status", "error", "Error: " + err.message);
  }
}

// ── Render results ────────────────────────────────────────────────────────────
function renderResults(beforeScore, afterScore, resumeText) {
  optimizedResumeText = resumeText;
  show("step3");

  const beforeVal = document.getElementById("score-before-val");
  const afterVal = document.getElementById("score-after-val");

  if (beforeScore) {
    beforeVal.textContent = beforeScore.overall_score;
    beforeVal.style.color = scoreColor(beforeScore.overall_score);
    renderBreakdown("score-breakdown", afterScore);
    renderAnalysis(afterScore);
  } else {
    document.getElementById("score-before").style.display = "none";
    document.querySelector(".score-arrow").style.display = "none";
  }

  afterVal.textContent = afterScore.overall_score;
  afterVal.style.color = scoreColor(afterScore.overall_score);
  document.getElementById("optimized-text").textContent = resumeText;

  if (!beforeScore) {
    renderBreakdown("score-breakdown", afterScore);
    renderAnalysis(afterScore);
  }

  document.getElementById("step3").scrollIntoView({ behavior: "smooth" });
}

function scoreColor(n) {
  if (n >= 75) return "var(--green)";
  if (n >= 50) return "var(--yellow)";
  return "var(--red)";
}

function renderBreakdown(containerId, score) {
  const rows = [
    ["Keywords", score.keyword_score],
    ["Skills", score.skills_score],
    ["Experience", score.experience_score],
    ["Education", score.education_score],
  ];
  document.getElementById(containerId).innerHTML = rows.map(([label, val]) => `
    <div class="breakdown-row">
      <span class="breakdown-label">${label}</span>
      <div class="progress-bar">
        <div class="progress-fill" style="width:${val}%;background:${scoreColor(val)}"></div>
      </div>
      <span class="breakdown-val" style="color:${scoreColor(val)}">${val}</span>
    </div>`).join("");
}

function renderAnalysis(score) {
  document.getElementById("analysis-display").innerHTML = `
    <div class="analysis-grid">
      <div class="analysis-box green">
        <h3>Matched Keywords</h3>
        <ul>${(score.matched_keywords || []).map(k => `<li>${k}</li>`).join("") || "<li>None</li>"}</ul>
      </div>
      <div class="analysis-box red">
        <h3>Missing Keywords</h3>
        <ul>${(score.missing_keywords || []).map(k => `<li>${k}</li>`).join("") || "<li>None</li>"}</ul>
      </div>
      <div class="analysis-box green">
        <h3>Matched Skills</h3>
        <ul>${(score.matched_skills || []).map(k => `<li>${k}</li>`).join("") || "<li>None</li>"}</ul>
      </div>
      <div class="analysis-box red">
        <h3>Missing Skills</h3>
        <ul>${(score.missing_skills || []).map(k => `<li>${k}</li>`).join("") || "<li>None</li>"}</ul>
      </div>
      <div class="analysis-box green">
        <h3>Strengths</h3>
        <ul>${(score.strengths || []).map(k => `<li>${k}</li>`).join("") || "<li>None</li>"}</ul>
      </div>
      <div class="analysis-box red">
        <h3>Gaps</h3>
        <ul>${(score.gaps || []).map(k => `<li>${k}</li>`).join("") || "<li>None</li>"}</ul>
      </div>
    </div>`;
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function show(id) { document.getElementById(id).classList.remove("hidden"); }

function copyResume() {
  navigator.clipboard.writeText(optimizedResumeText).then(() => alert("Copied!"));
}

function downloadResume() {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([optimizedResumeText], { type: "text/plain" }));
  a.download = "optimized_resume.txt";
  a.click();
}
