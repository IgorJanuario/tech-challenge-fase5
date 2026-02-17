#!/usr/bin/env python3
"""
STRIDE Threat Modeling Tool
============================
Reads an architecture diagram image, extracts system components using a vision LLM
(OpenAI GPT-4o via LangChain), and generates a comprehensive STRIDE threat modeling report.

Usage:
    python stride_threat_model.py --image diagram.png
    python stride_threat_model.py --image diagram.png --output my_report.md
"""

import argparse
import time
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# LangChain imports
# ---------------------------------------------------------------------------
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


# ============================================================================
# Image helpers
# ============================================================================

def load_image_as_base64(image_path: str) -> tuple[str, str]:
    """Read an image file and return (base64_string, mime_type)."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    ext = path.suffix.lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    mime_type = mime_map.get(ext, "image/png")

    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, mime_type




# ============================================================================
# LLM — Component Extraction
# ============================================================================

COMPONENT_EXTRACTION_PROMPT = """Você é um especialista em arquitetura de nuvem e software.
Analise a imagem de diagrama de arquitetura de sistema fornecida e identifique TODOS os componentes visíveis nela.

Para cada componente, forneça:
1. **nome**: Um nome descritivo (ex: "API Gateway", "Banco de Dados PostgreSQL", "S3 Bucket")
2. **tipo**: A categoria — um de: Usuário, Cliente, Servidor Web, Servidor de Aplicação, API Gateway, 
   Load Balancer, Banco de Dados, Cache, Fila de Mensagens, Armazenamento, CDN, DNS, Firewall, WAF, 
   Provedor de Identidade, Função Serverless, Contêiner, Microsserviço, Serviço de Terceiros, 
   Rede, VPN, Monitoramento, Logging, CI/CD, Outro
3. **provedor**: Nome do serviço de provedor de nuvem se identificável (ex: "AWS EC2", "Azure SQL", "Google Cloud Run"), caso contrário "Genérico"
4. **descrição**: Uma breve descrição de seu papel na arquitetura
5. **conexões**: Lista de nomes de outros componentes aos quais este componente se conecta, e o tipo de dados fluindo

IMPORTANTE: Retorne sua resposta como **JSON válido apenas**, com esta estrutura exata:
{{
  "components": [
    {{
      "name": "...",
      "type": "...",
      "provider": "...",
      "description": "...",
      "connections": [
        {{"target": "...", "data_flow": "..."}}
      ]
    }}
  ],
  "architecture_summary": "Um resumo de 2-3 frases da arquitetura geral"
}}

Retorne APENAS o objeto JSON, sem cercas markdown, sem texto extra.
"""


def extract_components(
    llm: ChatOpenAI,
    image_b64: str,
    mime_type: str,
) -> dict:
    """Send the diagram image to the LLM and extract architecture components."""

    prompt_text = COMPONENT_EXTRACTION_PROMPT

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt_text},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
            },
        ]
    )

    print("[LLM] Extracting components from the diagram …")
    response = llm.invoke([message])
    raw = response.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]  # remove first line
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("[WARN] LLM response was not valid JSON. Attempting repair …")
        # Try to find JSON object in the response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
        raise ValueError(f"Could not parse LLM response as JSON:\n{raw}")


# ============================================================================
# LLM — STRIDE Analysis
# ============================================================================

STRIDE_ANALYSIS_PROMPT = """Você é um especialista sênior em cibersegurança especializado em modelagem de ameaças.

Dados os seguintes componentes de arquitetura de sistema e suas conexões, realize uma 
análise abrangente de ameaças **STRIDE** para CADA componente.

## Componentes de Arquitetura
{components_json}

## Resumo da Arquitetura
{architecture_summary}

Para CADA componente, analise as seis categorias STRIDE:
- **S — Spoofing (Falsificação)**: Um atacante pode se passar por este componente ou por seus usuários?
- **T — Tampering (Adulteração)**: Os dados em trânsito ou em repouso podem ser modificados?
- **R — Repudiation (Repúdio)**: As ações podem ser executadas sem registro/auditoria adequados?
- **I — Information Disclosure (Divulgação de Informações)**: Os dados sensíveis podem ser expostos?
- **D — Denial of Service (Negação de Serviço)**: O componente pode ficar indisponível?
- **E — Elevation of Privilege (Elevação de Privilégio)**: Um atacante pode obter acesso/permissões não autorizados?

Para cada ameaça encontrada, forneça:
1. **ameaça**: Descrição da ameaça específica
2. **severidade**: Crítica, Alta, Média ou Baixa
3. **vulnerabilidades**: Vulnerabilidades específicas que habilitam esta ameaça
4. **contramedidas**: Contramedidas acionáveis para mitigar a ameaça

Retorne sua análise como **JSON válido apenas** com esta estrutura:
{{
  "stride_analysis": [
    {{
      "component_name": "...",
      "component_type": "...",
      "threats": [
        {{
          "category": "Spoofing|Tampering|Repudiation|Information Disclosure|Denial of Service|Elevation of Privilege",
          "threat": "...",
          "severity": "Crítica|Alta|Média|Baixa",
          "vulnerabilities": ["..."],
          "countermeasures": ["..."]
        }}
      ]
    }}
  ],
  "overall_risk_level": "Crítica|Alta|Média|Baixa",
  "executive_summary": "Um resumo executivo de 3-5 frases dos achados mais críticos"
}}

Retorne APENAS o objeto JSON, sem cercas markdown, sem texto extra.
"""


def analyze_stride(llm: ChatOpenAI, components_data: dict) -> dict:
    """Send extracted components to the LLM for STRIDE threat analysis."""

    components_json = json.dumps(components_data.get("components", []), indent=2)
    architecture_summary = components_data.get("architecture_summary", "N/A")

    prompt = STRIDE_ANALYSIS_PROMPT.format(
        components_json=components_json,
        architecture_summary=architecture_summary,
    )

    message = HumanMessage(content=prompt)
    print("[LLM] Performing STRIDE threat analysis …")
    response = llm.invoke([message])
    raw = response.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
        raise ValueError(f"Could not parse STRIDE response as JSON:\n{raw}")


# ============================================================================
# Report Generation
# ============================================================================

SEVERITY_EMOJI = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢",
}


def generate_report(
    components_data: dict,
    stride_data: dict,
    image_path: str,
    output_path: str,
) -> str:
    """Generate a professional Markdown STRIDE threat modeling report."""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    components = components_data.get("components", [])
    arch_summary = components_data.get("architecture_summary", "N/A")
    stride_analysis = stride_data.get("stride_analysis", [])
    exec_summary = stride_data.get("executive_summary", "N/A")
    overall_risk = stride_data.get("overall_risk_level", "N/A")

    lines: list[str] = []

    # -- Header --
    lines.append("# 🛡️ Relatório de Modelagem de Ameaças STRIDE")
    lines.append("")
    lines.append(f"**Gerado em:** {now}  ")
    lines.append(f"**Diagrama de Origem:** `{image_path}`  ")
    lines.append(f"**Nível de Risco Geral:** {SEVERITY_EMOJI.get(overall_risk, '⚪')} **{overall_risk}**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # -- Executive Summary --
    lines.append("## 📋 Resumo Executivo")
    lines.append("")
    lines.append(exec_summary)
    lines.append("")

    # -- Architecture Overview --
    lines.append("## 🏗️ Visão Geral da Arquitetura")
    lines.append("")
    lines.append(arch_summary)
    lines.append("")

    # -- Identified Components --
    lines.append("## 🧩 Componentes Identificados")
    lines.append("")
    lines.append("| # | Componente | Tipo | Provedor | Descrição |")
    lines.append("|---|-----------|------|----------|-----------|")
    for i, comp in enumerate(components, 1):
        lines.append(
            f"| {i} | **{comp.get('name', 'N/A')}** | {comp.get('type', 'N/A')} "
            f"| {comp.get('provider', 'N/A')} | {comp.get('description', 'N/A')} |"
        )
    lines.append("")

    # -- Data Flow --
    lines.append("## 🔄 Fluxo de Dados")
    lines.append("")
    for comp in components:
        connections = comp.get("connections", [])
        if connections:
            lines.append(f"### {comp['name']}")
            for conn in connections:
                target = conn.get("target", "?")
                flow = conn.get("data_flow", "?")
                lines.append(f"- → **{target}**: {flow}")
            lines.append("")

    # -- STRIDE Analysis --
    lines.append("---")
    lines.append("")
    lines.append("## 🔍 Análise de Ameaças STRIDE")
    lines.append("")

    for entry in stride_analysis:
        comp_name = entry.get("component_name", "Desconhecido")
        comp_type = entry.get("component_type", "Desconhecido")
        threats = entry.get("threats", [])

        lines.append(f"### 🔹 {comp_name} ({comp_type})")
        lines.append("")

        if not threats:
            lines.append("_Nenhuma ameaça significativa identificada._")
            lines.append("")
            continue

        lines.append("| Categoria | Ameaça | Severidade | Vulnerabilidades | Contramedidas |")
        lines.append("|-----------|--------|-----------|-------------------|----|")

        for t in threats:
            cat = t.get("category", "N/A")
            threat_desc = t.get("threat", "N/A")
            sev = t.get("severity", "N/A")
            emoji = SEVERITY_EMOJI.get(sev, "⚪")
            vulns = "; ".join(t.get("vulnerabilities", []))
            counters = "; ".join(t.get("countermeasures", []))
            lines.append(
                f"| **{cat}** | {threat_desc} | {emoji} {sev} | {vulns} | {counters} |"
            )

        lines.append("")

    # -- Risk Matrix --
    lines.append("---")
    lines.append("")
    lines.append("## 📊 Matriz de Resumo de Risco")
    lines.append("")

    # Count threats by severity
    severity_counts = {"Crítica": 0, "Alta": 0, "Média": 0, "Baixa": 0, "Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    category_counts = {}
    for entry in stride_analysis:
        for t in entry.get("threats", []):
            sev = t.get("severity", "Baixa")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            cat = t.get("category", "Outro")
            category_counts[cat] = category_counts.get(cat, 0) + 1

    lines.append("### Por Severidade")
    lines.append("")
    lines.append("| Severidade | Quantidade |")
    lines.append("|----------|-------|")
    for sev in ["Crítica", "Alta", "Média", "Baixa", "Critical", "High", "Medium", "Low"]:
        emoji = SEVERITY_EMOJI.get(sev, "⚪")
        if emoji != "⚪":
            lines.append(f"| {emoji} {sev} | {severity_counts.get(sev, 0)} |")
    lines.append("")

    lines.append("### Por Categoria STRIDE")
    lines.append("")
    lines.append("| Categoria | Quantidade |")
    lines.append("|----------|-------|")
    for cat in [
        "Spoofing", "Tampering", "Repudiation",
        "Information Disclosure", "Denial of Service", "Elevation of Privilege",
    ]:
        lines.append(f"| {cat} | {category_counts.get(cat, 0)} |")
    lines.append("")

    # -- Footer --
    lines.append("---")
    lines.append("")
    lines.append(
        "*Este relatório foi gerado automaticamente usando análise de arquitetura com IA "
        "e modelagem de ameaças STRIDE. Os achados devem ser revisados e validados por um "
        "profissional de segurança qualificado.*"
    )
    lines.append("")

    report = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    return report


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="STRIDE Threat Modeling Tool — Analyze architecture diagrams with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stride_threat_model.py --image aws_diagram.png
  python stride_threat_model.py --image diagram.jpg --output report.md
        """,
    )
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Path to the architecture diagram image (PNG, JPG, etc.)",
    )

    parser.add_argument(
        "--output", "-o",
        default="stride_report.md",
        help="Output path for the generated report (default: stride_report.md)",
    )
    parser.add_argument(
        "--openai-model",
        default="gpt-4o",
        help="OpenAI model name (default: gpt-4o)",
    )

    args = parser.parse_args()

    # -- Validate inputs --
    if not Path(args.image).exists():
        print(f"[ERROR] Image file not found: {args.image}")
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY environment variable is not set.")
        print("        Set it via: export OPENAI_API_KEY='your-key-here'")
        print("        Or create a .env file with: OPENAI_API_KEY=your-key-here")
        sys.exit(1)

    # -- Initialize LLM --
    print(f"[INIT] Using model: {args.openai_model}")
    llm = ChatOpenAI(
        model=args.openai_model,
        api_key=api_key,
        temperature=0.2,
    )

    # -- Step 1: Load image --
    print(f"[STEP 1/3] Loading image: {args.image}")
    image_b64, mime_type = load_image_as_base64(args.image)

    # -- Step 2: Extract components --
    print("[STEP 2/3] Extracting architecture components …")
    components_data = extract_components(llm, image_b64, mime_type)
    num_components = len(components_data.get("components", []))
    print(f"         Found {num_components} component(s).")

    time.sleep(10)

    # -- Step 3: STRIDE analysis --
    print("[STEP 3/3] Performing STRIDE threat analysis …")
    stride_data = analyze_stride(llm, components_data)
    total_threats = sum(
        len(entry.get("threats", []))
        for entry in stride_data.get("stride_analysis", [])
    )
    print(f"         Identified {total_threats} threat(s).")

    time.sleep(10)

    # -- Generate report --
    print(f"\n[REPORT] Generating report → {args.output}")
    generate_report(components_data, stride_data, args.image, args.output)

    print(f"\n✅ Done! Report saved to: {args.output}")
    print(f"   Components analyzed: {num_components}")
    print(f"   Threats identified:  {total_threats}")
    print(f"   Overall risk level:  {stride_data.get('overall_risk_level', 'N/A')}")


if __name__ == "__main__":
    main()
