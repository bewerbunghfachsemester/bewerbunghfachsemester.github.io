"""Schreibt die Uni-Daten aus unis.json in Startseite und Losverfahren-Seite.

Aufruf (im Projektordner):  python3 _daten/build_site.py
Ersetzt nur die datengetriebenen Blöcke (Tabellen, Uni-Karten, Liste ohne Losverfahren,
Download-Link). Alle übrigen Texte der Seiten bleiben unverändert.
"""

import logging
import re

from common import (
    PDF_URL, ROOT_DIR, SCOPE_ALSO_HIGHER, contact_html, display_name, esc,
    link_html, load_data, portal_url, scope_badge,
)
from uni_page import SECTION_PATH

LOGGER = logging.getLogger("build_site")

INDEX_FILE = ROOT_DIR / "index.html"
LOS_FILE = ROOT_DIR / "losverfahren" / "index.html"

LABEL_PORTAL = "Zum Portal"
LABEL_LOS_PAGE = "Zur Losverfahren-Seite"
LABEL_DOWNLOAD = "Uni-Liste als PDF &darr;"
CAPTION_START = "Bewerbung höheres Fachsemester Medizin – {count} Universitäten (Stand {stand})"
CAPTION_LOS = "Losverfahren Medizin – Loszeiträume nach Universität (Stand {stand})"
DOWNLOAD_NOTE = (
    'Die komplette Liste mit allen Fristen, Kontakten und klickbaren Links gibt es auch '
    '<a href="{url}" download>als PDF zum Herunterladen</a>.'
)
HIGHER_NOTE = (
    "<strong>Wichtig für Wechsler:</strong> Die meisten Universitäten verlosen nur Plätze im "
    "1. Fachsemester. Ausdrücklich auch für höhere Fachsemester gilt das Losverfahren nach "
    "aktuellem Stand nur hier: {names}. Für alle anderen bewirbst du dich regulär über die "
    '<a href="/#liste">Uni-Liste</a>.'
)
SCOPE_CSS = "      .gilt {\n        display: block;\n        font-size: 12px;\n        color: var(--muted);\n      }\n"


def replace_block(text, start_marker, end_marker, new_inner, anchor):
    """Ersetzt den Inhalt zwischen zwei Markern, gesucht ab einem Anker (z. B. id="liste")."""
    anchor_pos = text.index(anchor)
    start = text.index(start_marker, anchor_pos) + len(start_marker)
    end = text.index(end_marker, start)
    return text[:start] + new_inner + text[end:]


def replace_marked(text, name, new_inner, insert_before):
    """Ersetzt einen per Kommentar markierten Block oder fügt ihn einmalig ein."""
    begin, finish = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    block = f"{begin}\n{new_inner}\n        {finish}"
    if begin in text:
        return re.sub(re.escape(begin) + r".*?" + re.escape(finish), lambda _: block, text, flags=re.S)
    return text.replace(insert_before, f"{block}\n        {insert_before}", 1)


def subpage(uni):
    """Pfad der eigenen Uni-Unterseite."""
    return f"{SECTION_PATH}{uni['id']}/"


def subpage_link(uni):
    return f'              <a href="{subpage(uni)}">Alle Infos zu {esc(uni["kurz"])} &rarr;</a>'


def los_cell(uni):
    los = uni["los"]
    text = link_html(los["ws"], los["url"]) if los["url"] else esc(los["ws"])
    badge = scope_badge(los["gilt"])
    return text + (f'<span class="gilt">{esc(badge)}</span>' if badge else "")


def start_rows(unis):
    rows = [
        "\n              <tr>\n"
        f'                <th scope="row"><a href="{subpage(uni)}">{esc(display_name(uni))}</a></th>\n'
        f"                <td>{esc(uni['ss'])}</td>\n"
        f"                <td>{esc(uni['ws'])}</td>\n"
        f"                <td>{esc(uni['art'])}</td>\n"
        f"                <td>{link_html(LABEL_PORTAL, portal_url(uni))}</td>\n"
        f"                <td>{los_cell(uni)}</td>\n"
        "              </tr>"
        for uni in unis
    ]
    return "".join(rows) + "\n            "


def fact(label, value_html):
    return f"              <dt>{label}</dt>\n              <dd>{value_html}</dd>\n"


def start_card(uni):
    los = uni["los"]
    los_text = f"{esc(los['ws'])} (WiSe) · {esc(los['ss'])} (SoSe)"
    facts = (
        fact("Bewerbung SS", esc(uni["ss"])) + fact("Bewerbung WS", esc(uni["ws"]))
        + fact("Nachreichfrist", esc(uni["nach"])) + fact("Art", esc(uni["art"]))
        + fact("Losverfahren", los_text) + fact("Kontakt", contact_html(uni))
        + (fact("Postadresse", esc(uni["post"])) if uni.get("post") else "")
    )
    note = f'            <p class="uni-note">{esc(uni["hinweis"])}</p>\n' if uni.get("hinweis") else ""
    links = "\n".join(f"              {link_html(label, url, '↗' if url.startswith('http') else '↑')}" for label, url in uni["links"])
    los_link = f"\n              {link_html('Losverfahren', los['url'], '↗')}" if los["url"] else ""
    return (
        f'\n          <article class="uni-card" id="{esc(uni["id"])}">\n'
        f"            <h3>{esc(uni['name'])}</h3>\n"
        f'            <dl class="uni-facts">\n{facts}            </dl>\n{note}'
        f'            <p class="uni-links">\n{subpage_link(uni)}\n{links}{los_link}\n            </p>\n'
        "          </article>\n"
    )


def los_rows(unis):
    rows = [
        "\n              <tr>\n"
        f'                <th scope="row">{esc(display_name(uni))}</th>\n'
        f"                <td>{esc(uni['los']['ws'])}</td>\n"
        f"                <td>{esc(uni['los']['ss'])}</td>\n"
        f"                <td>{esc(uni['los']['gilt'])}</td>\n"
        f"                <td>{link_html('Offizielle Seite', uni['los']['url']) if uni['los']['url'] else '–'}</td>\n"
        "              </tr>"
        for uni in unis
    ]
    return "".join(rows) + "\n            "


def los_head(data):
    columns = ("Universität", data["semester_ws"], data["semester_ss"], "Gilt für", "Offizielle Seite")
    cells = "".join(f'                <th scope="col">{esc(column)}</th>\n' for column in columns)
    return f"\n              <tr>\n{cells}              </tr>\n            "


def los_card(uni):
    los = uni["los"]
    official = f'\n              {link_html(LABEL_LOS_PAGE, los["url"], "↗")}' if los["url"] else ""
    link = f'            <p class="uni-links">\n{subpage_link(uni)}{official}\n            </p>\n'
    return (
        f'\n          <article class="uni-card" id="{esc(uni["id"])}">\n'
        f"            <h3>Losverfahren {esc(display_name(uni))}</h3>\n"
        '            <dl class="uni-facts">\n'
        + fact("WiSe", esc(los["ws"])) + fact("SoSe", esc(los["ss"])) + fact("Gilt für", esc(los["gilt"]))
        + f"            </dl>\n{link}          </article>\n"
    )


def build_index(data):
    unis = data["unis"]
    text = INDEX_FILE.read_text(encoding="utf-8")
    text = replace_block(text, "<tbody>", "</tbody>", start_rows(unis), 'id="liste"')
    text = replace_block(text, '<div class="uni-grid">', "\n        </div>\n      </section>",
                         "".join(start_card(uni) for uni in unis), 'id="details"')
    text = re.sub(r"Bewerbung höheres Fachsemester Medizin –\s+\d+ Universitäten \(Stand\s+[^)]*\)",
                  CAPTION_START.format(count=len(unis), stand=data["stand"]), text)
    text = re.sub(r'<th scope="col">Losverfahren[^<]*</th>', f'<th scope="col">Losverfahren ({data["semester_ws"]})</th>', text)
    text = re.sub(r'<a\s+class="cta"\s+href="[^"]*"[^>]*>[^<]*</a\s*>',
                  f'<a class="cta" href="{PDF_URL}" download>{LABEL_DOWNLOAD}</a>', text, count=1)
    text = re.sub(r"Stand: \w+ 2026", f"Stand: {data['stand']}", text)
    text = replace_marked(text, "pdf-download", f'        <p class="note">{DOWNLOAD_NOTE.format(url=PDF_URL)}</p>',
                          '<div class="table-scroll">')
    if ".gilt {" not in text:
        text = text.replace("    </style>", SCOPE_CSS + "    </style>", 1)
    INDEX_FILE.write_text(text, encoding="utf-8")
    LOGGER.info("Startseite aktualisiert: %d Universitäten", len(unis))


def build_losverfahren(data):
    unis = data["unis"]
    listed = [uni for uni in unis if not uni["los"].get("ohne")]
    without = [uni for uni in unis if uni["los"].get("ohne")]
    higher = ", ".join(uni["name"] for uni in unis if uni["los"]["gilt"] == SCOPE_ALSO_HIGHER)
    text = LOS_FILE.read_text(encoding="utf-8")
    text = replace_block(text, "<thead>", "</thead>", los_head(data), 'id="tabelle"')
    text = replace_block(text, "<tbody>", "</tbody>", los_rows(listed), 'id="tabelle"')
    text = replace_block(text, '<div class="uni-grid">', "\n        </div>\n      </section>",
                         "".join(los_card(uni) for uni in unis), 'id="unis"')
    items = "".join(f"\n          <li>{esc(display_name(uni))} – {esc(uni['los']['ohne'])}</li>" for uni in without)
    text = replace_block(text, '<ul class="plain">', "</ul>", items + "\n        ", 'id="ohne"')
    text = re.sub(r"Losverfahren höheres Fachsemester Medizin – Loszeiträume nach\s+Universität \(Stand[^)]*\)",
                  CAPTION_LOS.format(stand=data["stand"]), text)
    text = re.sub(r"Losverfahren Medizin – Loszeiträume nach Universität \(Stand[^)]*\)",
                  CAPTION_LOS.format(stand=data["stand"]), text)
    text = re.sub(r"Stand: \w+ 2026", f"Stand: {data['stand']}", text)
    text = replace_marked(text, "hfs-hinweis", f'        <div class="note">{HIGHER_NOTE.format(names=higher)}</div>',
                          '<div class="table-scroll">')
    LOS_FILE.write_text(text, encoding="utf-8")
    LOGGER.info("Losverfahren-Seite aktualisiert: %d mit, %d ohne Losverfahren", len(listed), len(without))


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    data = load_data()
    build_index(data)
    build_losverfahren(data)


if __name__ == "__main__":
    main()
