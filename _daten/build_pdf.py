"""Erzeugt die herunterladbare Uni-Liste als PDF mit klickbaren Links.

Aufruf (im Projektordner):  python3 _daten/build_pdf.py
Rendert eine HTML-Fassung aus unis.json und druckt sie mit Google Chrome (headless) als PDF.
"""

import logging
import subprocess
from pathlib import Path

from common import (
    BUILD_DIR, PDF_PATH, contact_html, display_name, esc, link_html, load_data,
)

LOGGER = logging.getLogger("build_pdf")

CHROME_BINARY = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
HTML_PATH = BUILD_DIR / "uni-liste.html"

TITLE = "Uni-Liste: Bewerbung ins höhere Fachsemester Medizin"
SUBTITLE = "Stand {stand} · kostenlos und unabhängig von bewerbungsrenner.com"
INTRO = (
    "Alle Links in dieser Liste sind klickbar. SS = Sommersemester, WS = Wintersemester, "
    "FS = Fachsemester. Losverfahren: „nur 1. FS“ heißt, dass dort nur Erstsemesterplätze verlost werden."
)
DISCLAIMER = (
    "Alle Angaben ohne Gewähr. Universitäten ändern Fristen, Portale und Anforderungen – bitte vor jeder "
    "Bewerbung die verlinkte offizielle Seite prüfen. Fragen oder Korrekturen: "
    '<a href="mailto:bewerbung.h.fachsemester@gmail.com">bewerbung.h.fachsemester@gmail.com</a> · '
    '<a href="https://www.bewerbungsrenner.com/">www.bewerbungsrenner.com</a>'
)
COLUMNS = ("Universität", "Bewerbung SS", "Bewerbung WS", "Nachreichfrist", "Art", "Kontakt", "Losverfahren", "Links")

STYLES = """
@page { size: A4 landscape; margin: 11mm 10mm 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Helvetica Neue", Arial, sans-serif; font-size: 8.4pt; color: #111; }
h1 { margin: 0; font-size: 17pt; letter-spacing: -0.01em; }
.sub { margin: 2pt 0 6pt; font-size: 9pt; color: #444; }
.intro { margin: 0 0 8pt; font-size: 8pt; color: #333; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th:nth-child(1) { width: 17%; } th:nth-child(2), th:nth-child(3) { width: 7.5%; }
th:nth-child(4) { width: 10%; } th:nth-child(5) { width: 7.5%; } th:nth-child(6) { width: 14.5%; }
th:nth-child(7) { width: 20%; } th:nth-child(8) { width: 16%; }
td { overflow-wrap: anywhere; }
thead th { text-align: left; font-size: 7.4pt; text-transform: uppercase; letter-spacing: 0.04em;
  color: #444; border-bottom: 1.2pt solid #111; padding: 4pt 4pt; }
tbody td { vertical-align: top; padding: 4pt 4pt; border-bottom: 0.5pt solid #ccc; }
tr { break-inside: avoid; }
.name { font-weight: 700; font-size: 8.8pt; }
.hint { display: block; margin-top: 2pt; font-size: 7.3pt; color: #444; }
.scope { display: block; font-size: 7.3pt; color: #444; }
.scope.higher { color: #111; font-weight: 700; }
a { color: #0b4fb3; text-decoration: none; }
.links a { display: block; padding: 2.5pt 0; }
.links a + a { border-top: 0.6pt solid #b9b9b9; }
.foot { margin-top: 8pt; font-size: 7.4pt; color: #444; }
"""


def los_html(los):
    scope_class = "scope higher" if los["gilt"] == "auch höhere FS" else "scope"
    period = f"WiSe: {esc(los['ws'])}<br>SoSe: {esc(los['ss'])}"
    return f'{period}<span class="{scope_class}">Gilt für: {esc(los["gilt"])}</span>'


def links_html(uni):
    entries = [link_html(label, url) for label, url in uni["links"] if url.startswith("http")]
    if uni["los"]["url"]:
        entries.append(link_html("Losverfahren", uni["los"]["url"]))
    return "".join(entries)


def row_html(uni):
    hint = f'<span class="hint">{esc(uni["hinweis"])}</span>' if uni.get("hinweis") else ""
    post = f'<span class="hint">Post: {esc(uni["post"])}</span>' if uni.get("post") else ""
    cells = (
        f'<td><span class="name">{esc(display_name(uni))}</span>{hint}</td>',
        f"<td>{esc(uni['ss'])}</td>", f"<td>{esc(uni['ws'])}</td>", f"<td>{esc(uni['nach'])}</td>",
        f"<td>{esc(uni['art'])}</td>", f"<td>{contact_html(uni)}{post}</td>",
        f"<td>{los_html(uni['los'])}</td>", f'<td class="links">{links_html(uni)}</td>',
    )
    return "<tr>" + "".join(cells) + "</tr>"


def document_html(data):
    head = "".join(f"<th>{esc(column)}</th>" for column in COLUMNS)
    rows = "\n".join(row_html(uni) for uni in data["unis"])
    return (
        f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{esc(TITLE)}</title>'
        f"<style>{STYLES}</style></head><body>"
        f"<h1>{esc(TITLE)}</h1><p class=\"sub\">{esc(SUBTITLE.format(stand=data['stand']))}</p>"
        f'<p class="intro">{esc(INTRO)}</p>'
        f"<table><thead><tr>{head}</tr></thead><tbody>\n{rows}\n</tbody></table>"
        f'<p class="foot">{DISCLAIMER}</p></body></html>'
    )


def print_pdf(html_path, pdf_path):
    if not CHROME_BINARY.exists():
        raise FileNotFoundError(f"Google Chrome nicht gefunden: {CHROME_BINARY}")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(CHROME_BINARY), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri(),
    ]
    subprocess.run(command, check=True, capture_output=True, timeout=120)


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    data = load_data()
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(document_html(data), encoding="utf-8")
    print_pdf(HTML_PATH, PDF_PATH)
    LOGGER.info("PDF erstellt: %s (%d Universitäten)", PDF_PATH, len(data["unis"]))


if __name__ == "__main__":
    main()
