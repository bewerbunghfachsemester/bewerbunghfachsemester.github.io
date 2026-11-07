"""Erzeugt die Uni-Unterseiten /hoeheres-fachsemester/<id>/ und die sitemap.xml.

Aufruf (im Projektordner):  python3 _daten/build_unis.py
Das Seitendesign (CSS) wird aus der Losverfahren-Seite übernommen, damit alle Seiten gleich aussehen.
"""

import datetime
import logging
import re

from common import ROOT_DIR, esc, load_data
from uni_page import SECTION_PATH, SITE_URL, page_html

LOGGER = logging.getLogger("build_unis")

STYLE_SOURCE = ROOT_DIR / "losverfahren" / "index.html"
SECTION_DIR = ROOT_DIR / SECTION_PATH.strip("/")
SITEMAP_FILE = ROOT_DIR / "sitemap.xml"
STATIC_PAGES = (("/", "1.0"), ("/losverfahren/", "0.9"), ("/medizin-restplaetze/", "0.8"))
UNI_PAGE_PRIORITY = "0.7"

HUB_HTML = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Höheres Fachsemester Medizin – alle Universitäten</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{site}/">
<meta http-equiv="refresh" content="0; url=/#liste">
</head>
<body>
<p>Weiter zur <a href="/#liste">Uni-Liste</a>.</p>
<ul>{items}</ul>
</body>
</html>
"""


def site_css():
    """Übernimmt den CSS-Block der Losverfahren-Seite."""
    text = STYLE_SOURCE.read_text(encoding="utf-8")
    match = re.search(r"<style>(.*?)</style>", text, re.S)
    if not match:
        raise ValueError(f"Kein <style>-Block in {STYLE_SOURCE}")
    return match.group(1)


def sitemap_xml(unis, today):
    urls = [(path, priority) for path, priority in STATIC_PAGES]
    urls += [(f"{SECTION_PATH}{uni['id']}/", UNI_PAGE_PRIORITY) for uni in unis]
    entries = "".join(
        f"  <url>\n    <loc>{SITE_URL}{path}</loc>\n    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n    <priority>{priority}</priority>\n  </url>\n"
        for path, priority in urls
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + "</urlset>\n")


def write_pages(data, css, today):
    for uni in data["unis"]:
        target = SECTION_DIR / uni["id"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page_html(uni, data, css, today), encoding="utf-8")
    items = "".join(f'<li><a href="{SECTION_PATH}{uni["id"]}/">{esc(uni["name"])}</a></li>' for uni in data["unis"])
    (SECTION_DIR / "index.html").write_text(HUB_HTML.format(site=SITE_URL, items=items), encoding="utf-8")


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    data = load_data()
    today = datetime.date.today().isoformat()
    write_pages(data, site_css(), today)
    SITEMAP_FILE.write_text(sitemap_xml(data["unis"], today), encoding="utf-8")
    LOGGER.info("%d Uni-Seiten und sitemap.xml geschrieben (lastmod %s)", len(data["unis"]), today)


if __name__ == "__main__":
    main()
