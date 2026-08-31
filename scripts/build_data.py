#!/usr/bin/env python3
"""
build_data.py — coração do pipeline do CONTRATE A ARTE.

O que faz:
  1. Lê a "planilha" (CSV exportado do Google Sheets, ou o CSV mock local).
  2. Filtra só as linhas com status == "aprovado" e consentimento_publicacao == TRUE.
  3. Valida os campos mínimos obrigatórios (nome, área, pelo menos 1 canal de contato).
  4. Gera um id (slug) estável por artista.
  5. Comprime/redimensiona a foto de cada artista (webp, lado maior 640px).
  6. Escreve src/_data/artistas.json — consumido pelo Eleventy no build do site.
  7. Escreve src/_data/stats.json — números agregados para o relatório de impacto do edital.

Por design, este script NÃO fala com a internet (Google Sheets API) ainda — lê um CSV local.
Isso é proposital: a Fase 0 prova o pipeline "CSV -> JSON -> fotos" de ponta a ponta antes de
plugar a API do Google, que exige credenciais que só existem depois que a planilha real for criada.

Quando a planilha real existir, troque a função `carregar_linhas()` por uma chamada à Sheets API
(fica isolada nesta função de propósito — é o único lugar que muda).
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow não instalado. Rode: pip install Pillow", file=sys.stderr)
    raise

RAIZ = Path(__file__).resolve().parent.parent
CSV_ENTRADA = RAIZ / "data" / "mock_planilha_exemplo.csv"
FOTOS_ENTRADA = RAIZ / "data" / "fotos_pendentes"
FOTOS_SAIDA = RAIZ / "src" / "img" / "artistas"
JSON_SAIDA = RAIZ / "src" / "_data" / "artistas.json"
STATS_SAIDA = RAIZ / "src" / "_data" / "stats.json"

FOTO_LADO_MAX = 640          # px — suficiente para mobile-first, mantém o site leve
FOTO_PLACEHOLDER = "sem-foto.svg"

CAMPOS_OBRIGATORIOS = ("nome_artistico", "area_atuacao")


@dataclass
class Artista:
    id: str
    nome_artistico: str
    municipio: str = ""
    regiao: str = ""
    area_atuacao: list[str] = field(default_factory=list)
    especialidades: list[str] = field(default_factory=list)
    bio: str = ""
    tempo_atuacao_anos: str = ""
    trajetoria: str = ""
    projetos: list[str] = field(default_factory=list)
    premiacoes: list[str] = field(default_factory=list)
    editais: list[str] = field(default_factory=list)
    portfolio_links: list[str] = field(default_factory=list)
    instagram: str = ""
    youtube: str = ""
    spotify: str = ""
    outros_links: list[str] = field(default_factory=list)
    whatsapp: str = ""
    email: str = ""
    foto: str = FOTO_PLACEHOLDER


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto or "artista"


def slug_unico(base: str, usados: set[str]) -> str:
    slug = base
    contador = 2
    while slug in usados:
        slug = f"{base}-{contador}"
        contador += 1
    usados.add(slug)
    return slug


def lista_de(campo: str) -> list[str]:
    """Campos multi-valor vêm separados por '|' na planilha (ex.: 'MC|Batalha de rima')."""
    if not campo:
        return []
    return [item.strip() for item in campo.split("|") if item.strip()]


def carregar_linhas() -> list[dict]:
    """Fonte dos dados. Hoje: CSV local. Amanhã: Google Sheets API (trocar só aqui)."""
    if not CSV_ENTRADA.exists():
        print(f"Arquivo não encontrado: {CSV_ENTRADA}", file=sys.stderr)
        sys.exit(1)
    with CSV_ENTRADA.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def linha_valida(linha: dict) -> tuple[bool, str]:
    if linha.get("status", "").strip().lower() != "aprovado":
        return False, "status != aprovado"
    if linha.get("consentimento_publicacao", "").strip().upper() != "TRUE":
        return False, "sem consentimento de publicação explícito"
    for campo in CAMPOS_OBRIGATORIOS:
        if not linha.get(campo, "").strip():
            return False, f"campo obrigatório ausente: {campo}"
    tem_contato = any(linha.get(c, "").strip() for c in ("whatsapp", "email", "instagram"))
    if not tem_contato:
        return False, "nenhum canal de contato preenchido (whatsapp/email/instagram)"
    return True, ""


def processar_foto(nome_arquivo: str, slug: str) -> str:
    """Comprime a foto para webp, lado maior <= FOTO_LADO_MAX. Retorna o nome do arquivo final."""
    if not nome_arquivo:
        return FOTO_PLACEHOLDER
    origem = FOTOS_ENTRADA / nome_arquivo
    if not origem.exists():
        print(f"  aviso: foto '{nome_arquivo}' não encontrada em {FOTOS_ENTRADA}, usando placeholder")
        return FOTO_PLACEHOLDER

    FOTOS_SAIDA.mkdir(parents=True, exist_ok=True)
    destino = FOTOS_SAIDA / f"{slug}.webp"
    with Image.open(origem) as img:
        img = img.convert("RGB")
        img.thumbnail((FOTO_LADO_MAX, FOTO_LADO_MAX))
        img.save(destino, "WEBP", quality=80)
    return destino.name


def montar_artista(linha: dict, slug: str) -> Artista:
    return Artista(
        id=slug,
        nome_artistico=linha["nome_artistico"].strip(),
        municipio=linha.get("municipio", "").strip(),
        regiao=linha.get("regiao", "").strip(),
        area_atuacao=lista_de(linha.get("area_atuacao", "")),
        especialidades=lista_de(linha.get("especialidades", "")),
        bio=linha.get("bio", "").strip(),
        tempo_atuacao_anos=linha.get("tempo_atuacao_anos", "").strip(),
        trajetoria=linha.get("trajetoria", "").strip(),
        projetos=lista_de(linha.get("projetos", "")),
        premiacoes=lista_de(linha.get("premiacoes", "")),
        editais=lista_de(linha.get("editais", "")),
        portfolio_links=lista_de(linha.get("portfolio_links", "")),
        instagram=linha.get("instagram", "").strip(),
        youtube=linha.get("youtube", "").strip(),
        spotify=linha.get("spotify", "").strip(),
        outros_links=lista_de(linha.get("outros_links", "")),
        whatsapp=linha.get("whatsapp", "").strip(),
        email=linha.get("email", "").strip(),
        foto=processar_foto(linha.get("foto_arquivo", "").strip(), slug),
    )


def gerar_stats(artistas: list[Artista]) -> dict:
    areas = {a for art in artistas for a in art.area_atuacao}
    municipios = {art.municipio for art in artistas if art.municipio}
    com_portfolio = sum(1 for art in artistas if art.portfolio_links)
    return {
        "artistas_publicados": len(artistas),
        "areas_representadas": len(areas),
        "municipios_representados": len(municipios),
        "perfis_com_portfolio": com_portfolio,
        "lista_areas": sorted(areas),
        "lista_municipios": sorted(municipios),
    }


def main() -> None:
    linhas = carregar_linhas()
    usados: set[str] = set()
    artistas: list[Artista] = []
    ignorados = 0

    for linha in linhas:
        ok, motivo = linha_valida(linha)
        nome = linha.get("nome_artistico", "(sem nome)")
        if not ok:
            print(f"  ignorado '{nome}': {motivo}")
            ignorados += 1
            continue
        slug = slug_unico(slugify(linha["nome_artistico"]), usados)
        artistas.append(montar_artista(linha, slug))
        print(f"  publicado: {nome} -> id={slug}")

    JSON_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    JSON_SAIDA.write_text(
        json.dumps([a.__dict__ for a in artistas], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    STATS_SAIDA.write_text(
        json.dumps(gerar_stats(artistas), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n{len(artistas)} perfis publicados, {ignorados} ignorados.")
    print(f"-> {JSON_SAIDA.relative_to(RAIZ)}")
    print(f"-> {STATS_SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
