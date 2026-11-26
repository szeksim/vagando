const CATEGORIAS = [
  "HR & Talent Acquisition",
  "Learning & Development",
  "Quality Assurance",
  "Non-profit, Social Impact & Sustainability",
  "Customer Experience & Operations",
  "Project & Business Operations"
];

const state = { jobs: [], query: "", category: "", eligibility: "", source: "" };
const $ = (id) => document.getElementById(id);

function safeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);
}
function dateLabel(value) {
  if (!value) return "Data não informada";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? "Data não informada" :
    new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" }).format(d);
}
function populateFilters() {
  CATEGORIAS.forEach(name => $("category").add(new Option(name, name)));
  [...new Set(state.jobs.map(j => j.source).filter(Boolean))].sort()
    .forEach(name => $("source").add(new Option(name, name)));
}
function render() {
  const q = state.query.toLocaleLowerCase("pt-BR");
  const filtered = state.jobs.filter(job => {
    const haystack = [job.title, job.company, job.description, job.category, ...(job.tags || [])].join(" ").toLocaleLowerCase("pt-BR");
    return (!q || haystack.includes(q)) &&
      (!state.category || job.category === state.category) &&
      (!state.eligibility || (job.eligibility || []).includes(state.eligibility)) &&
      (!state.source || job.source === state.source);
  });
  $("result-count").textContent = `${filtered.length} de ${state.jobs.length} oportunidades`;
  $("jobs").innerHTML = filtered.length ? filtered.map(job => `
    <article class="job-card">
      <div class="card-top">
        <span class="company">${safeText(job.company || "Organização não informada")}</span>
        <span class="pill">${safeText(job.category)}</span>
      </div>
      <h3>${safeText(job.title)}</h3>
      <div class="meta">
        ${(job.eligibility || []).map(x => `<span>🌍 ${safeText(x)}</span>`).join("")}
        ${job.employment_type ? `<span>· ${safeText(job.employment_type)}</span>` : ""}
        ${job.location ? `<span>· ${safeText(job.location)}</span>` : ""}
      </div>
      <p class="description">${safeText(job.description || "Acesse a publicação original para consultar os detalhes da oportunidade.").slice(0, 230)}${(job.description || "").length > 230 ? "…" : ""}</p>
      <div class="card-bottom">
        <small>${safeText(job.source)} · ${dateLabel(job.date_posted || job.date_found)}</small>
        <a class="apply" href="${safeText(job.url)}" target="_blank" rel="noopener noreferrer">Ver oportunidade ↗</a>
      </div>
    </article>`).join("") : `<p class="empty">Nenhuma oportunidade encontrada com esses filtros. Experimente alterar sua busca.</p>`;
}
async function init() {
  try {
    const response = await fetch("data/jobs.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Não foi possível carregar os dados");
    const data = await response.json();
    state.jobs = data.jobs || [];
    $("job-count").textContent = state.jobs.length;
    $("updated-at").textContent = data.updated_at ? dateLabel(data.updated_at) : "Ainda não atualizado";
    populateFilters();
    render();
  } catch (error) {
    $("jobs").innerHTML = `<p class="empty">Não foi possível carregar os dados do radar. Tente novamente mais tarde.</p>`;
    $("result-count").textContent = "";
  }
}
$("search").addEventListener("input", e => { state.query = e.target.value; render(); });
$("category").addEventListener("change", e => { state.category = e.target.value; render(); });
$("eligibility").addEventListener("change", e => { state.eligibility = e.target.value; render(); });
$("source").addEventListener("change", e => { state.source = e.target.value; render(); });
init();
