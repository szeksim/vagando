#!/usr/bin/env python3
"""Coleta oportunidades de APIs públicas e publica apenas vagas com sinal geográfico explícito."""
from __future__ import annotations
import json, re, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "jobs.json"

CATEGORIAS = {
    "HR & Talent Acquisition": [
        "talent acquisition", "recruiter", "recruiting", "people operations", "people ops",
        "human resources", " hr ", "people partner", "hrbp", "people experience",
        "recrutamento", "recrutador", "recursos humanos", "gestão de pessoas"
    ],
    "Learning & Development": [
        "learning and development", "learning & development", "instructional design",
        "instructional designer", "learning experience", "enablement", "training", "lms",
        "talent development", "organizational development", "aprendizagem", "desenvolvimento",
        "treinamento", "designer instrucional", "educação corporativa"
    ],
    "Quality Assurance": [
        "quality assurance", "quality analyst", "quality specialist", "quality manager", "quality operations", "quality control", "quality management",
        "qa analyst", "qa specialist", "qa manager", "quality monitoring", "quality improvement", "process quality", "service quality", "support quality",
        "garantia da qualidade", "analista de qualidade", "monitoria de qualidade", "gestão da qualidade", "controle de qualidade", "melhoria contínua"
    ],
    "Non-profit, Social Impact & Sustainability": [
        "nonprofit", "non-profit", "non profit", "social impact", "humanitarian",
        "international development", "animal welfare", "animal rights", "animal advocacy",
        "animal protection", "wildlife", "conservation", "climate", "sustainability",
        "environment", "biodiversity", "environmental", "bem-estar animal", "proteção animal",
        "direitos dos animais", "meio ambiente", "sustentabilidade", "conservação",
        "impacto social", "terceiro setor", "desenvolvimento internacional"
    ],
    "Customer Experience & Operations": [
        "customer experience", "customer success", "customer support", "customer education",
        "change management", "knowledge management", "support operations", "cx operations", "service operations",
        "experiência do cliente", "sucesso do cliente", "suporte ao cliente"
    ],
    "1. Project & Business Operations": [
        "project manager", "program manager", "program management", "business operations",
        "business analyst", "operations manager", "strategy and operations", "ai operations",
        "project coordinator", "program operations", "gerente de projetos", "gestão de projetos",
        "operações de negócios", "analista de negócios"
    ]
}

def buscar_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "VagandoRadar/0.1 (public job discovery)"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

def limpar_html(valor: str) -> str:
    valor = re.sub(r"<[^>]+>", " ", valor or "")
    return re.sub(r"\s+", " ", unescape(valor)).strip()

def classificar(titulo: str, descricao: str, tags: list[str]) -> str | None:
    texto = f" {titulo} {descricao} {' '.join(tags)} ".lower()
    for categoria, palavras in CATEGORIAS.items():
        if any(palavra in texto for palavra in palavras):
            return categoria
    return None

def identificar_elegibilidade(texto: str) -> list[str]:
    texto = (texto or "").lower()
    elegibilidade = []
    if re.search(r"\b(brazil|brasil)\b", texto):
        elegibilidade.append("Brasil")
    if re.search(r"\b(latin america|latam|south america|central america)\b", texto):
        elegibilidade.append("América Latina")
    if re.search(r"\b(worldwide|work from anywhere|anywhere in the world|global remote|globally)\b", texto):
        elegibilidade.append("Mundo")
    return elegibilidade

def normalizar(fonte, titulo, empresa, url, localidade, descricao, tags, publicado,
               tipo_contrato=None, remoto=True):
    if not titulo or not url or not remoto:
        return None
    elegibilidade = identificar_elegibilidade(localidade + " " + descricao[:1200])
    if not elegibilidade:
        return None
    categoria = classificar(titulo, descricao, tags)
    if not categoria:
        return None
    identificador = re.sub(r"[^a-z0-9]+", "-", f"{fonte}-{empresa}-{titulo}".lower()).strip("-")[:120]
    return {
        "id": identificador, "title": titulo.strip(),
        "company": empresa.strip() or "Organização não informada",
        "category": categoria, "eligibility": elegibilidade,
        "location": localidade.strip()[:120], "employment_type": tipo_contrato,
        "source": fonte, "url": url, "date_posted": publicado,
        "date_found": datetime.now(timezone.utc).isoformat(),
        "description": descricao[:1200], "tags": tags[:15]
    }

def coletar_remotive():
    dados = buscar_json("https://remotive.com/api/remote-jobs?limit=500")
    vagas = []
    for item in dados.get("jobs", []):
        vaga = normalizar(
            "Remotive", item.get("title", ""), item.get("company_name", ""), item.get("url", ""),
            item.get("candidate_required_location", ""), limpar_html(item.get("description", "")),
            item.get("tags", []), item.get("publication_date"), item.get("job_type"), True
        )
        if vaga: vagas.append(vaga)
    return vagas

def coletar_arbeitnow():
    dados = buscar_json("https://www.arbeitnow.com/api/job-board-api")
    vagas = []
    for item in dados.get("data", []):
        vaga = normalizar(
            "Arbeitnow", item.get("title", ""), item.get("company_name", ""), item.get("url", ""),
            item.get("location", ""), limpar_html(item.get("description", "")),
            item.get("tags", []), item.get("created_at"), None, bool(item.get("remote", False))
        )
        if vaga: vagas.append(vaga)
    return vagas

def main():
    coletadas, erros = [], []
    for nome, coletor in [("Remotive", coletar_remotive), ("Arbeitnow", coletar_arbeitnow)]:
        try:
            coletadas.extend(coletor())
            print(f"{nome}: coleta concluída")
        except Exception as erro:
            erros.append(f"{nome}: {type(erro).__name__}: {erro}")
            print(erros[-1])

    unicas = {}
    for vaga in coletadas:
        chave = (vaga["company"].lower(), vaga["title"].lower())
        unicas.setdefault(chave, vaga)

    vagas = sorted(unicas.values(), key=lambda item: item.get("date_posted") or "", reverse=True)
    resultado = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(vagas), "source_errors": erros, "jobs": vagas
    }
    OUT.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(vagas)} oportunidades elegíveis salvas em {OUT}")

if __name__ == "__main__":
    main()
