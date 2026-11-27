#!/usr/bin/env python3
"""Coleta oportunidades de APIs públicas e publica apenas vagas com sinal geográfico explícito."""
from __future__ import annotations
import json, re, os, urllib.request, urllib.error, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "jobs.json"

CATEGORIAS = {
    "HR & Talent Acquisition": [
        "talent acquisition", "talent partner", "recruiter", "recruiting",
        "people operations", "people ops", "people partner",
        "people experience", "human resources", "hr manager",
        "hr business partner", "hrbp", "recruitment",
        "recrutamento", "recrutador", "recursos humanos",
        "gestão de pessoas", "business partner de rh"
    ],

    "Learning & Development": [
        "learning and development", "learning & development",
        "instructional design", "instructional designer",
        "learning experience", "learning specialist",
        "learning manager", "learning enablement",
        "talent development", "organizational development",
        "corporate learning", "corporate training",
        "training manager", "training specialist",
        "trainer", "enablement",
        "employee enablement",
        "sales training", "learning consultant",
        "learning experience designer", "curriculum development",
        "learning operations", "aprendizagem", "treinamento",
        "designer instrucional", "educação corporativa",
        "desenvolvimento organizacional"
    ],

    "Quality Assurance": [
        "quality assurance", "quality analyst", "quality specialist",
        "quality manager", "quality operations", "quality control",
        "quality management", "qa analyst", "qa specialist",
        "qa manager", "qa engineer", "quality monitoring",
        "quality improvement", "process quality", "service quality",
        "support quality", "quality auditor", "qa operations",
        "quality coach", "quality lead", "quality assurance lead",
        "garantia da qualidade", "analista de qualidade",
        "monitoria de qualidade", "gestão da qualidade",
        "controle de qualidade", "melhoria contínua"
    ],

    "Non-profit, Social Impact & Sustainability": [
        "nonprofit", "non-profit", "nonprofit organization",
        "nonprofit management", "social impact",
        "humanitarian", "international development",
        "animal welfare", "animal rights", "animal advocacy",
        "animal protection", "animal shelter", "animal rescue",
        "animal care", "wildlife protection", "wildlife conservation",
        "climate action", "climate change",
        "environmental protection", "environmental conservation",
        "biodiversity conservation",
        "environmental sustainability",
        "sustainable development",
        "bem-estar animal", "proteção animal", "direitos dos animais",
        "resgate animal", "proteção da fauna",
        "meio ambiente", "sustentabilidade ambiental",
        "conservação ambiental", "mudanças climáticas",
        "impacto social", "terceiro setor",
        "desenvolvimento internacional",
        "organização sem fins lucrativos"
    ],

    "Customer Experience & Operations": [
        "customer experience", "customer experience manager",
        "head of customer experience", "customer success",
        "customer success manager", "head of customer success",
        "customer support", "customer support manager",
        "customer service", "customer service manager",
        "head of support", "head of customer support",
        "support manager", "support lead",
        "support team lead", "support specialist",
        "support operations", "customer operations",
        "customer operations manager",
        "customer care", "client success",
        "client success manager", "client experience",
        "client services", "client services manager",
        "cx operations", "cx manager",
        "service operations", "service delivery manager",
        "knowledge management", "knowledge manager",
        "customer education", "customer onboarding",
        "customer enablement", "customer advocacy",
        "experiência do cliente", "sucesso do cliente",
        "suporte ao cliente", "atendimento ao cliente",
        "gerente de suporte", "gerente de atendimento",
        "coordenação de atendimento", "gestão de suporte",
        "operações de atendimento", "gestão de conhecimento",
        "experiência do consumidor", "relacionamento com clientes"
    ],

    "Project & Business Operations": [
        "project manager", "program manager",
        "project management", "program management",
        "project coordinator", "program coordinator",
        "project operations", "program operations",
        "business operations", "business operations manager",
        "strategy and operations", "project lead",
        "program lead", "portfolio manager", "pmo",
        "ai operations", "gerente de projetos",
        "gestão de projetos", "coordenação de projetos",
        "gestão de programas", "operações de negócios",
        "analista de negócios"
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
    titulo = (titulo or "").lower()
    tags_texto = " ".join(tags or []).lower()

    termos_genericos = {
        "enablement",
        "trainer",
        "training"
    }

    resultados = {}

    for categoria, palavras in CATEGORIAS.items():
        correspondencias = [
            palavra for palavra in palavras
            if palavra not in termos_genericos
            and re.search(r"(?<!\w)" + re.escape(palavra) + r"(?!\w)", titulo)
        ]

        if not correspondencias:
            continue

        pontos_titulo = len(correspondencias) * 3

        pontos_tags = sum(
            1 for palavra in palavras
            if palavra not in termos_genericos
            and re.search(r"(?<!\w)" + re.escape(palavra) + r"(?!\w)", tags_texto)
        )

        resultados[categoria] = pontos_titulo + pontos_tags

    if not resultados:
        return None

    maior_pontuacao = max(resultados.values())

    melhores = [
        categoria
        for categoria, pontos in resultados.items()
        if pontos == maior_pontuacao
    ]

    if len(melhores) != 1:
        return None

    return melhores[0]
    
def identificar_localizacao(localidade: str, descricao: str = "", fonte: str = "") -> list[str]:
    local = (localidade or "").lower()
    texto = (descricao or "").lower()
    
    # Disponibilidade mundial informada na localidade
    if re.search(r"\b(worldwide|global|anywhere)\b", local):
        return ["Mundo"]

    # Disponibilidade mundial explicitamente declarada
    if re.search(
        r"\b(worldwide|work from anywhere|anywhere in the world|global remote|globally)\b",
        texto
    ):
        return ["Mundo"]

    # Disponibilidade explícita para Brasil
    if re.search(
        r"\b(remote in brazil|based anywhere in brazil|brazil-based candidates|candidates in brazil|brazil|brasil)\b",
        local
    ) or re.search(
        r"\b(remote in brazil|based anywhere in brazil|brazil-based candidates|candidates in brazil)\b",
        texto
    ):
        return ["Brasil"]

    # Disponibilidade explícita para América Latina
    if re.search(
        r"\b(latin america|latam|south america|central america)\b",
        local
    ) or re.search(
        r"\b(candidates in latin america|based in latin america|remote across latin america)\b",
        texto
    ):
        return ["América Latina"]

    # Remotive: a localidade representa a elegibilidade exigida
    paises_restritos = (
        r"\b(usa|u\.s\.a\.?|united states|united kingdom|uk|"
        r"germany|deutschland|france|canada|australia|"
        r"netherlands|switzerland|ireland|spain|portugal)\b"
    )

    if fonte == "Remotive" and re.search(paises_restritos, local):
        return []

    # Arbeitnow: a localidade pode representar apenas a sede ou cidade.
    # Procuramos restrições explícitas na descrição.
    restricoes_explicitas = (
        r"\b(only applicants? (?:based|located|residing) in|"
        r"must be based in|must reside in|must live in|"
        r"residents? of|based exclusively in|"
        r"located exclusively in|remote within|"
        r"remote only in|remote from|"
        r"eligible to work in|authorized to work in|"
        r"right to work in|work authorization in)\s+"
        r"(?:the\s+)?(united states|usa|uk|united kingdom|"
        r"germany|deutschland|france|canada|australia|"
        r"netherlands|switzerland|ireland|spain|portugal)\b"
    )

    if re.search(restricoes_explicitas, texto):
        return []

    # Sem informação suficiente: manter para revisão
    return ["A confirmar"]

estatisticas = {
    "dados_remoto": 0,
    "elegibilidade": 0,
    "categoria": 0,
    "aprovadas": 0
}
def normalizar(fonte, titulo, empresa, url, localidade, descricao, tags, publicado,
               tipo_contrato=None, remoto=True):

    if not titulo or not url or not remoto:
        estatisticas["dados_remoto"] += 1
        print(f"[DESCARTADA: dados/remoto] {titulo}")
        return None

    elegibilidade = identificar_localizacao(
        localidade,
        descricao[:5000],
        fonte
    )
    if not elegibilidade:
        estatisticas["elegibilidade"] += 1
        print(f"[DESCARTADA: elegibilidade] {titulo} | Local: {localidade}")
        return None

    categoria = classificar(titulo, descricao, tags)
    if not categoria:
        estatisticas["categoria"] += 1
        print(f"[DESCARTADA: categoria] {titulo} | Tags: {tags[:5]}")
        return None

    estatisticas["aprovadas"] += 1

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


def coletar_himalayas():
    vagas = []
    cursor = None
    paginas = 0
    limite_paginas = 10

    chave = os.environ.get("HIMALAYAS_API_KEY")

    if not chave:
        print("[Himalayas] Chave de API não encontrada.")
        return vagas

    while paginas < limite_paginas:
        parametros = {"limit": 20}

        if cursor:
            parametros["cursor"] = cursor

        url = (
            "https://himalayas.app/jobs/api?"
            + urllib.parse.urlencode(parametros)
        )

        requisicao = urllib.request.Request(
            url,
            headers={
                "User-Agent": "VagandoRadar/0.1",
                "Authorization": f"Bearer {chave}"
            }
        )

        try:
            with urllib.request.urlopen(requisicao, timeout=30) as resposta:
                dados = json.loads(resposta.read().decode("utf-8"))

        except urllib.error.HTTPError as erro:
            print(
                f"[Himalayas] Erro HTTP {erro.code} "
                f"na página {paginas + 1}: {erro.reason}"
            )
            break

        except Exception as erro:
            print(
                f"[Himalayas] Erro na página {paginas + 1}: {erro}"
            )
            break

        resultados = dados.get("jobs", [])

        if not resultados:
            break

        paginas += 1

        for item in resultados:
            restricoes = item.get("locationRestrictions")
            fusos = item.get("timezoneRestrictions")

            # Sem os campos geográficos, não presumimos elegibilidade.
            if restricoes is None or fusos is None:
                localidade = "A confirmar"

            else:
                restricoes = [pais.lower() for pais in restricoes]

                # Fusos brasileiros: UTC-5, UTC-4, UTC-3 e UTC-2.
                fusos_brasil = {-5, -4, -3, -2}

                fuso_compativel = (
                    not fusos
                    or bool(set(fusos) & fusos_brasil)
                )

                brasil_permitido = (
                    not restricoes
                    or "brazil" in restricoes
                )

                if not brasil_permitido or not fuso_compativel:
                    continue

                if not restricoes and not fusos:
                    localidade = "Worldwide"
                else:
                    localidade = "Brazil"

            descricao = limpar_html(
                item.get("description") or item.get("excerpt", "")
            )

            vaga = normalizar(
                "Himalayas",
                item.get("title", ""),
                item.get("companyName", ""),
                item.get("applicationLink", ""),
                localidade,
                descricao,
                item.get("categories", []),
                item.get("pubDate"),
                item.get("employmentType"),
                True
            )

            if vaga:
                vagas.append(vaga)

        cursor = dados.get("nextCursor")

        if not cursor:
            break

    print(
        f"[Himalayas] {paginas} páginas consultadas; "
        f"{len(vagas)} vagas aprovadas."
    )

    return vagas

def main():
    coletadas, erros = [], []

    print("\n========== RELATÓRIO VAGANDO ==========\n")

    for nome, coletor in [
        ("Remotive", coletar_remotive),
        ("Arbeitnow", coletar_arbeitnow),
        ("Himalayas", coletar_himalayas)
    ]:
        try:
            vagas_fonte = coletor()
            coletadas.extend(vagas_fonte)

            print(
                f"{nome}: {len(vagas_fonte)} vagas "
                "passaram por todos os filtros."
            )

        except Exception as erro:
            erros.append(
                f"{nome}: {type(erro).__name__}: {erro}"
            )
            print(f"ERRO - {erros[-1]}")

    total_coletado = len(coletadas)

    unicas = {}

    for vaga in coletadas:
        chave = (
            vaga["company"].lower(),
            vaga["title"].lower()
        )
        unicas.setdefault(chave, vaga)

    vagas = sorted(
        unicas.values(),
        key=lambda item: str(item.get("date_posted") or ""),
        reverse=True
    )

    duplicadas = total_coletado - len(vagas)

    resultado = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(vagas),
        "source_errors": erros,
        "jobs": vagas
    }

    OUT.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("\n---------- RESUMO ----------")
    print(f"Descartadas por dados/remoto: {estatisticas['dados_remoto']}")
    print(f"Descartadas por elegibilidade: {estatisticas['elegibilidade']}")
    print(f"Descartadas por categoria: {estatisticas['categoria']}")
    print(f"Aprovadas: {estatisticas['aprovadas']}")
    print(f"Total aprovado pelas fontes: {total_coletado}")
    print(f"Duplicidades removidas: {duplicadas}")
    print(f"Total publicado: {len(vagas)}")
    print(f"Erros encontrados: {len(erros)}")
    print("============================\n")

if __name__ == "__main__":
    main()
