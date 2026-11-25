const CATEGORY_LABELS = [
  "HR & Talent Acquisition",
  "Learning & Development",
  "Non-profit, Social Impact & Sustainability",
  "Customer Experience & Operations",
  "Project & Business Operations"
];

const state = { jobs: [], query: "", category: "", eligibility: "", source: "" };
const $ = (id) => document.getElementById(id);

function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);
}
function dateLabel(value) {
  if (!value) return "Date not provided";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? "Date not provided" :
    new Intl.DateTimeFormat("en", { day: "numeric", month: "short", year: "numeric" }).format(d);
}
function populateFilters() {
  CATEGORY_LABELS.forEach((name) => $("category").add(new Option(name, name)));
  [...new Set(state.jobs.map(j => j.source).filter(Boolean))].sort().forEach(name => $("source").add(new Option(name, name)));
}
function render() {
  const q = state.query.toLowerCase();
  const filtered = state.jobs.filter(job => {
    const haystack = [job.title, job.company, job.description, job.category, ...(job.tags || [])].join(" ").toLowerCase();
    return (!q || haystack.includes(q)) &&
      (!state.category || job.category === state.category) &&
      (!state.eligibility || (job.eligibility || []).includes(state.eligibility)) &&
      (!state.source || job.source === state.source);
  });
  $("result-count").textContent = `${filtered.length} of ${state.jobs.length} opportunities`;
  $("jobs").innerHTML = filtered.length ? filtered.map(job => `
    <article class="job-card">
      <div class="card-top">
        <span class="company">${safeText(job.company || "Company not listed")}</span>
        <span class="pill">${safeText(job.category)}</span>
      </div>
      <h3>${safeText(job.title)}</h3>
      <div class="meta">
        ${(job.eligibility || []).map(x => `<span>🌍 ${safeText(x)}</span>`).join("")}
        ${job.employment_type ? `<span>· ${safeText(job.employment_type)}</span>` : ""}
        ${job.location ? `<span>· ${safeText(job.location)}</span>` : ""}
      </div>
      <p class="description">${safeText(job.description || "Open the original listing for role details.").slice(0, 230)}${(job.description || "").length > 230 ? "…" : ""}</p>
      <div class="card-bottom">
        <small>${safeText(job.source)} · ${dateLabel(job.date_posted || job.date_found)}</small>
        <a class="apply" href="${safeText(job.url)}" target="_blank" rel="noopener noreferrer">View job ↗</a>
      </div>
    </article>`).join("") : `<p class="empty">No matching opportunities yet. Try changing your filters.</p>`;
}
async function init() {
  try {
    const response = await fetch("data/jobs.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Could not load jobs data");
    const data = await response.json();
    state.jobs = data.jobs || [];
    $("job-count").textContent = state.jobs.length;
    $("updated-at").textContent = data.updated_at ? dateLabel(data.updated_at) : "Not yet";
    populateFilters();
    render();
  } catch (error) {
    $("jobs").innerHTML = `<p class="empty">The radar data could not be loaded. Please try again later.</p>`;
    $("result-count").textContent = "";
  }
}
$("search").addEventListener("input", e => { state.query = e.target.value; render(); });
$("category").addEventListener("change", e => { state.category = e.target.value; render(); });
$("eligibility").addEventListener("change", e => { state.eligibility = e.target.value; render(); });
$("source").addEventListener("change", e => { state.source = e.target.value; render(); });
init();
