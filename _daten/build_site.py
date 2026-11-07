"""Schreibt die Uni-Daten aus unis.json in Startseite und Losverfahren-Seite.

Aufruf (im Projektordner):  python3 _daten/build_site.py
Ersetzt nur Blöcke zwischen Markierungen wie <!-- uni-liste:start --> … <!-- uni-liste:end -->.
Alle übrigen Texte der Seiten bleiben unverändert.
"""

import logging
import re

from blocks import (
    los_list_html, ohne_items_html, season_strip_html, ticker_html, timeline_html, uni_list_html,
)
from common import ROOT_DIR, SCOPE_ALSO_HIGHER, load_data

LOGGER = logging.getLogger("build_site")

INDEX_FILE = ROOT_DIR / "index.html"
LOS_FILE = ROOT_DIR / "losverfahren" / "index.html"

HIGHER_NOTE = (
    '<div class="note"><strong>Wichtig für Wechsler:</strong> Die meisten Universitäten verlosen nur Plätze im '
    "1. Fachsemester. Ausdrücklich auch für höhere Fachsemester gilt das Losverfahren nach aktuellem Stand nur "
    'hier: {names}. Für alle anderen bewirbst du dich regulär über die <a href="/#liste">Uni-Liste</a>.</div>'
)


class MarkerMissingError(ValueError):
    """Eine erwartete Markierung fehlt in der Seite."""


def fill_marker(text, name, inner):
    """Ersetzt den Inhalt zwischen <!-- name:start --> und <!-- name:end -->."""
    begin, finish = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if begin not in text or finish not in text:
        raise MarkerMissingError(f"Markierung „{name}“ fehlt")
    pattern = re.escape(begin) + r".*?" + re.escape(finish)
    return re.sub(pattern, lambda _: f"{begin}{inner}{finish}", text, count=1, flags=re.S)


def update_stand(text, stand):
    return re.sub(r"Stand: \w+ 2026", f"Stand: {stand}", text)


def build_index(data):
    text = INDEX_FILE.read_text(encoding="utf-8")
    text = fill_marker(text, "jahr", timeline_html())
    text = fill_marker(text, "ticker", ticker_html(data["unis"]))
    text = fill_marker(text, "uni-liste", uni_list_html(data))
    INDEX_FILE.write_text(update_stand(text, data["stand"]), encoding="utf-8")
    LOGGER.info("Startseite aktualisiert: %d Universitäten", len(data["unis"]))


def build_losverfahren(data):
    unis = data["unis"]
    listed = [uni for uni in unis if not uni["los"].get("ohne")]
    without = [uni for uni in unis if uni["los"].get("ohne")]
    higher = ", ".join(uni["name"] for uni in unis if uni["los"]["gilt"] == SCOPE_ALSO_HIGHER)
    text = LOS_FILE.read_text(encoding="utf-8")
    text = fill_marker(text, "saison", season_strip_html())
    text = fill_marker(text, "los-liste", HIGHER_NOTE.format(names=higher) + los_list_html(data, listed))
    text = fill_marker(text, "ohne", ohne_items_html(without))
    LOS_FILE.write_text(update_stand(text, data["stand"]), encoding="utf-8")
    LOGGER.info("Losverfahren-Seite aktualisiert: %d mit, %d ohne Losverfahren", len(listed), len(without))


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    data = load_data()
    build_index(data)
    build_losverfahren(data)


if __name__ == "__main__":
    main()
