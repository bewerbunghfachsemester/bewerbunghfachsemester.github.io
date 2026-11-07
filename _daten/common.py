"""Gemeinsame Helfer für die Erzeugung von Website-Tabellen und PDF aus unis.json."""

import html
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
ROOT_DIR = DATA_DIR.parent
DATA_FILE = DATA_DIR / "unis.json"
BUILD_DIR = DATA_DIR / "build"

PDF_FILENAME = "uni-liste-hoeheres-fachsemester-medizin.pdf"
PDF_PATH = ROOT_DIR / "downloads" / PDF_FILENAME
PDF_URL = "/downloads/" + PDF_FILENAME

SCOPE_ALSO_HIGHER = "auch höhere FS"
SCOPE_FIRST_ONLY = "nur 1. FS"
SCOPE_UNKNOWN = "keine Angabe"
SCOPE_NONE = "–"
KNOWN_SCOPES = (SCOPE_ALSO_HIGHER, SCOPE_FIRST_ONLY, SCOPE_UNKNOWN, SCOPE_NONE)

EXTERNAL_LINK_ATTRS = ' target="_blank" rel="noopener nofollow"'


def load_data(path=DATA_FILE):
    """Liest die zentrale Datendatei."""
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value):
    """HTML-sicherer Text, leere Werte werden zu ''."""
    return html.escape(value or "", quote=True)


def is_external(url):
    return url.startswith("http")


def link_html(label, url, arrow=""):
    """Link mit passenden Attributen für externe oder interne Ziele."""
    attrs = EXTERNAL_LINK_ATTRS if is_external(url) else ""
    suffix = f" {arrow}" if arrow else ""
    return f'<a href="{esc(url)}"{attrs}>{esc(label)}{suffix}</a>'


def display_name(uni):
    """Name mit Zusatz in Klammern, z. B. „Universität Augsburg (Modellstudiengang)“."""
    tag = uni.get("tag")
    return f"{uni['name']} ({tag})" if tag else uni["name"]


def contact_html(uni):
    """Kontakt als mailto-Link plus optionaler Zusatztext."""
    mail = uni.get("mail")
    extra = uni.get("kontakt")
    parts = []
    if mail:
        parts.append(f'<a href="mailto:{esc(mail)}">{esc(mail)}</a>')
    if extra:
        parts.append(esc(extra))
    return " ".join(parts) or "–"


def portal_url(uni):
    """Der erste Link einer Uni ist ihr Bewerbungsportal bzw. ihre Bewerbungsseite."""
    return uni["links"][0][1]


def scope_badge(scope):
    """Kurzer Hinweis, ob das Losverfahren auch für höhere Fachsemester gilt."""
    if scope in (SCOPE_ALSO_HIGHER, SCOPE_FIRST_ONLY):
        return scope
    return ""
