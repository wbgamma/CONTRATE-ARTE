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
import io
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow não instalado. Rode: pip install -r requirements.txt", file=sys.stderr)
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
    """Fonte dos dados: planilha real via Sheets API, se as credenciais estiverem
    configuradas (SHEETS_ID + SHEETS_SERVICE_ACCOUNT_JSON); senão cai pro CSV mock
    local, útil pra desenvolvimento/teste sem tocar na planilha de verdade."""
    if os.environ.get("SHEETS_ID") and os.environ.get("SHEETS_SERVICE_ACCOUNT_JSON"):
        print("Lendo respostas da planilha real via Sheets API...")
        return [normalizar_linha_sheets(l) for l in carregar_linhas_sheets()]

    print("SHEETS_ID/SHEETS_SERVICE_ACCOUNT_JSON não configurados — usando CSV mock local.")
    if not CSV_ENTRADA.exists():
        print(f"Arquivo não encontrado: {CSV_ENTRADA}", file=sys.stderr)
        sys.exit(1)
    with CSV_ENTRADA.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def carregar_linhas_sheets() -> list[dict]:
    """Lê a planilha real via Google Sheets API (service account). Cada linha vem
    como um dict com os cabeçalhos exatos das perguntas do Google Form."""
    import gspread
    from google.oauth2.service_account import Credentials

    escopos = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    credenciais = Credentials.from_service_account_info(
        json.loads(os.environ["SHEETS_SERVICE_ACCOUNT_JSON"]), scopes=escopos
    )
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(os.environ["SHEETS_ID"])
    aba = planilha.sheet1
    return aba.get_all_records()


def _campo_multivalor(texto: str, separador: str) -> str:
    """Junta um campo multi-valor da planilha real (vírgula ou quebra de linha,
    dependendo da pergunta) no mesmo formato '|' que lista_de() já espera."""
    if not texto:
        return ""
    return "|".join(p.strip() for p in texto.split(separador) if p.strip())


# Mapeia o cabeçalho exato de cada pergunta do Forms pra chave interna do script,
# e diz se o campo é multi-valor separado por vírgula ou por quebra de linha
# (ver docs/GOOGLE-FORM.md, seção "Nota técnica"). Ajustar aqui se o texto de
# alguma pergunta mudar no Forms — os dois precisam ficar em sincronia.
MAPA_COLUNAS_SHEETS = {
    "Nome artístico": ("nome_artistico", None),
    "Município": ("municipio", None),
    "Bairro, distrito ou região (sem endereço exato)": ("regiao", None),
    "Área de atuação": ("area_atuacao", ","),
    "Especialidades (ex.: DJ, Fotógrafo, MC, Grafiteiro, Produtor musical...)": ("especialidades", ","),
    "Bio curta (até ~300 caracteres)": ("bio", None),
    "Há quantos anos atua?": ("tempo_atuacao_anos", None),
    "Conte sua trajetória": ("trajetoria", None),
    "Projetos realizados (um por linha)": ("projetos", "\n"),
    "Premiações (um por linha)": ("premiacoes", "\n"),
    "Participação em editais/projetos culturais (um por linha)": ("editais", "\n"),
    "Link(s) de portfólio (um por linha)": ("portfolio_links", "\n"),
    "Instagram (usuário, sem @)": ("instagram", None),
    "YouTube (link do canal)": ("youtube", None),
    "Spotify (link do perfil/artista)": ("spotify", None),
    "Outros links relevantes (um por linha)": ("outros_links", "\n"),
    "WhatsApp profissional (com DDD)": ("whatsapp", None),
    "E-mail profissional": ("email", None),
    "Foto de perfil": ("foto_arquivo", None),
}


def normalizar_linha_sheets(bruta: dict) -> dict:
    """Converte uma linha crua da planilha (cabeçalhos = texto das perguntas do
    Forms) pro mesmo formato de dict que linha_valida()/montar_artista() já
    entendem (mesmas chaves e convenções do CSV mock)."""
    linha: dict = {"status": str(bruta.get("Status", "")).strip()}

    for cabecalho, (chave, separador) in MAPA_COLUNAS_SHEETS.items():
        valor = str(bruta.get(cabecalho, "") or "").strip()
        linha[chave] = _campo_multivalor(valor, separador) if separador else valor

    consentimento = str(bruta.get("Consentimento de publicação", "")).strip()
    linha["consentimento_publicacao"] = "TRUE" if consentimento else "FALSE"

    return linha


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


_CREDENCIAIS_GOOGLE = None


def _credenciais_google():
    """Credenciais da service account, reaproveitadas entre chamadas à Sheets e Drive API."""
    global _CREDENCIAIS_GOOGLE
    if _CREDENCIAIS_GOOGLE is None:
        from google.oauth2.service_account import Credentials

        _CREDENCIAIS_GOOGLE = Credentials.from_service_account_info(
            json.loads(os.environ["SHEETS_SERVICE_ACCOUNT_JSON"]),
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
    return _CREDENCIAIS_GOOGLE


def _extrair_id_drive(valor: str) -> str | None:
    """Extrai o id do arquivo a partir do jeito que o Forms grava a resposta de
    upload na planilha (link completo, ou às vezes só o id)."""
    m = re.search(r"[-\w]{25,}", valor)
    return m.group(0) if m else None


def _baixar_foto_drive(file_id: str, destino_dir: Path) -> Path | None:
    """Baixa uma foto enviada via upload do Forms (fica no Drive do dono do
    formulário). Exige que a service account tenha acesso de leitura ao arquivo/
    pasta — ver docs/RUNBOOK.md. Retorna None e loga aviso se não conseguir, pra
    não derrubar o build inteiro por causa de uma foto."""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload

        servico = build("drive", "v3", credentials=_credenciais_google(), cache_discovery=False)
        metadados = servico.files().get(fileId=file_id, fields="name,mimeType").execute()
        extensao = ".jpg" if "jpeg" in metadados.get("mimeType", "") else ".png"

        destino_dir.mkdir(parents=True, exist_ok=True)
        destino = destino_dir / f"{file_id}{extensao}"
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, servico.files().get_media(fileId=file_id))
        concluido = False
        while not concluido:
            _, concluido = downloader.next_chunk()
        destino.write_bytes(buffer.getvalue())
        return destino
    except Exception as e:  # noqa: BLE001 - qualquer falha aqui não pode derrubar o build
        print(f"  aviso: não foi possível baixar a foto do Drive (id={file_id}): {e}")
        return None


def processar_foto(referencia_foto: str, slug: str) -> str:
    """Comprime a foto para webp, lado maior <= FOTO_LADO_MAX. Retorna o nome do
    arquivo final. Aceita tanto um nome de arquivo local (modo CSV mock) quanto
    uma referência do Drive (modo Sheets API real - link ou id do upload)."""
    if not referencia_foto:
        return FOTO_PLACEHOLDER

    origem = FOTOS_ENTRADA / referencia_foto
    if not origem.exists():
        file_id = _extrair_id_drive(referencia_foto)
        if file_id and os.environ.get("SHEETS_SERVICE_ACCOUNT_JSON"):
            origem = _baixar_foto_drive(file_id, FOTOS_ENTRADA)
        else:
            origem = None

    if not origem or not Path(origem).exists():
        print(f"  aviso: foto '{referencia_foto}' não encontrada/baixável, usando placeholder")
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
