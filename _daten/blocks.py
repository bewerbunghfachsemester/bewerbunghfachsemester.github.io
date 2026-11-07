"""Datengetriebene Blöcke im neuen Design: Bewerbungsjahr, Laufband, Uni-Liste, Losverfahren-Liste."""

from common import (
    PDF_URL, SCOPE_ALSO_HIGHER, contact_html, display_name, esc, link_html,
)

SUBPAGE_PATH = "/hoeheres-fachsemester/"
MONTHS = ("Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez")
NO_WINDOW_PREFIXES = ("kein", "Medizin nicht", "über", "keine eigene", "Humanmedizin bisher", "bisher nie",
                      "Losverfahren Medizin durchgeführt", "noch", "Termin offen", "nur höhere", "–")
PLUS_ICON = ('<svg class="plus" viewBox="0 0 14 14" aria-hidden="true">'
             '<path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="1.6" fill="none"></path></svg>')
TIMELINE_TRACKS = (
    ("Bewerbung Sommersemester", (((1, 1), (1, 15), ""), ((1, 15), (3, 15), "ext"),
                                  ((10, 15), (12, 1), "ext"), ((12, 1), (13, 1), ""))),
    ("Bewerbung Wintersemester", (((5, 1), (6, 1), "ext"), ((6, 1), (7, 15), ""), ((7, 15), (9, 15), "ext"))),
    ("Losverfahren", (((2, 1), (5, 1), "los"), ((8, 1), (11, 1), "los"))),
)
TIMELINE_SUMMARY = ("Bewerbung zum Sommersemester meist vom 01.12. bis 15.01., an einzelnen Unis ab 15.10. oder bis "
                    "15.03. Bewerbung zum Wintersemester meist vom 01.06. bis 15.07., an einzelnen Unis ab 01.05. oder "
                    "bis 15.09. Losverfahren überwiegend von Februar bis April und von August bis Oktober.")


def year_percent(month, day):
    """Lage eines Datums im Jahr in Prozent (Monat 13 = Jahresende)."""
    days = {1: 0, 2: 31, 3: 59, 4: 90, 5: 120, 6: 151, 7: 181, 8: 212, 9: 243, 10: 273, 11: 304, 12: 334, 13: 365}
    return (days[month] + day - 1) / 365 * 100


def bar_html(start, end, kind, index):
    left = year_percent(*start)
    width = year_percent(*end) - left
    css_class = f"bar {kind}".strip()
    return (f'<span class="{css_class}" style="left:{left:.2f}%;width:{width:.2f}%;'
            f'--d:{0.45 + index * 0.09:.2f}s"></span>')


def today_marker_html():
    return ('<div class="jahr-today" data-today hidden><span class="today-label" data-today-label></span>'
            '<span class="today-line"></span><span class="today-dot"></span><span class="today-pulse"></span></div>')


def chart_frame(inner):
    grid = "".join("<span></span>" for _ in MONTHS)
    months = "".join(f"<span>{month}</span>" for month in MONTHS)
    return (f'<div class="jahr-chart" aria-hidden="true" data-today-chart>'
            f'<div class="jahr-grid">{grid}</div><div class="jahr-months">{months}</div>'
            f'<div class="jahr-progress"><span class="bar" style="--d:0.3s"></span></div>'
            f"{inner}{today_marker_html()}</div>")


def timeline_html():
    """Bewerbungsjahr der Startseite mit drei Spuren."""
    counter = iter(range(20))
    tracks = "".join(
        f'<div class="jahr-track"><p>{label}</p><div class="jahr-bars">'
        + "".join(bar_html(start, end, kind, next(counter)) for start, end, kind in bars)
        + "</div></div>"
        for label, bars in TIMELINE_TRACKS
    )
    legend = ('<ul class="legend"><li><span class="swatch"></span>Hauptfrist der meisten Unis</li>'
              '<li><span class="swatch ext"></span>abweichende Fristen einzelner Unis</li>'
              '<li><span class="swatch los"></span>Losverfahren (überwiegend)</li></ul>')
    return (f'<div class="jahr"><div class="jahr-head"><h2 id="jahr-titel">Das Bewerbungsjahr</h2>{legend}</div>'
            f'<p class="sr-only">{TIMELINE_SUMMARY}</p>{chart_frame(tracks)}</div>')


def season_strip_html():
    """Zeitleiste der Losverfahren-Seite: SS Februar–April, WS August–Oktober."""
    bars = (bar_html((2, 1), (5, 1), "los", 1) + bar_html((8, 1), (11, 1), "los", 2)
            + f'<span class="bar-label" style="left:calc({year_percent(2, 1):.2f}% + 10px)">Losverfahren SS</span>'
            + f'<span class="bar-label" style="left:calc({year_percent(8, 1):.2f}% + 10px)">Losverfahren WS</span>')
    head = ('<div class="jahr-head"><h2 id="saison-titel">Wann gelost wird</h2>'
            '<p class="legend">SS überwiegend Februar – April · WS überwiegend August – Oktober</p></div>')
    track = f'<div class="jahr-track"><div class="jahr-bars tall">{bars}</div></div>'
    return f'<div class="jahr">{head}{chart_frame(track)}</div>'


def ticker_html(unis):
    items = "".join(
        f'<span class="ticker-item">{esc(uni["name"])}<span>SS {esc(uni["ss"])} · WS {esc(uni["ws"])}</span></span>'
        for uni in unis + unis
    )
    return f'<div class="ticker" aria-hidden="true"><div class="ticker-track">{items}</div></div>'


def has_window(text):
    return not text.startswith(NO_WINDOW_PREFIXES)


def los_status(text):
    state = "on" if has_window(text) else "off"
    muted = "" if has_window(text) else " muted"
    return f'<span class="los"><span class="dot {state}" aria-hidden="true"></span><span class="num{muted}">{esc(text)}</span></span>'


def higher_tag(uni):
    return '<span class="tag higher">auch höhere FS</span>' if uni["los"]["gilt"] == SCOPE_ALSO_HIGHER else ""


def search_text(uni):
    return esc(" ".join(filter(None, (uni["name"], uni["kurz"], uni["id"], uni["land"], uni.get("tag")))))


def list_tools(input_id, target, count_label, extra=""):
    return (f'<div class="list-tools"><div class="search"><label for="{input_id}">Uni suchen</label>'
            f'<input id="{input_id}" type="search" placeholder="z. B. Heidelberg, Charité, Köln" autocomplete="off" '
            f'data-filter="#{target}"></div><div class="list-meta"><p aria-live="polite" data-filter-count>'
            f"{esc(count_label)}</p>{extra}</div></div>")


def fact(label, value_html):
    return f"<dt>{label}</dt><dd>{value_html}</dd>"


def uni_panel(uni):
    los = uni["los"]
    facts = (fact("Nachreichfrist", esc(uni["nach"])) + fact("Kontakt", contact_html(uni))
             + (fact("Postadresse", esc(uni["post"])) if uni.get("post") else "")
             + fact("Losverfahren SoSe", esc(los["ss"])) + fact("Losverfahren gilt für", esc(los["gilt"])))
    note = f'<p class="uni-note">{esc(uni["hinweis"])}</p>' if uni.get("hinweis") else ""
    links = [f'<a href="{SUBPAGE_PATH}{uni["id"]}/">Alle Infos zu {esc(uni["kurz"])} →</a>']
    links += [link_html(label, url, "↗" if url.startswith("http") else "↑") for label, url in uni["links"]]
    links += [link_html("Losverfahren", los["url"], "↗")] if los["url"] else []
    return (f'<div class="uni-panel"><dl class="uni-facts">{facts}</dl>{note}'
            f'<p class="uni-links">{"".join(links)}</p></div>')


def uni_item(uni):
    tag = f'<span class="tag">{esc(uni["tag"])}</span>' if uni.get("tag") else ""
    return (f'<details class="uni" id="{esc(uni["id"])}" data-search="{search_text(uni)}">'
            f'<summary class="uni-row"><span class="c-name">{PLUS_ICON}<span>{esc(uni["name"])}</span>{tag}</span>'
            f'<span><span class="mlabel">Frist SS</span><span class="num">{esc(uni["ss"])}</span></span>'
            f'<span><span class="mlabel">Frist WS</span><span class="num">{esc(uni["ws"])}</span></span>'
            f'<span><span class="mlabel">Art</span>{esc(uni["art"])}</span>'
            f'<span class="c-los"><span class="mlabel">Losverfahren</span>{los_status(uni["los"]["ws"])} {higher_tag(uni)}</span>'
            f"</summary>{uni_panel(uni)}</details>")


def uni_list_html(data):
    unis = data["unis"]
    count = f"{len(unis)} Universitäten · Stand {data['stand']}"
    pdf = f'<a class="chip" href="{PDF_URL}" download>Liste als PDF ↓</a>'
    head = ('<div class="list-head uni" aria-hidden="true"><span>Universität</span><span>Frist SS</span>'
            f'<span>Frist WS</span><span>Art</span><span>Losverfahren ({esc(data["semester_ws"])})</span></div>')
    items = "".join(uni_item(uni) for uni in unis)
    return (f'{list_tools("uni-suche", "uni-liste", count, pdf)}{head}<div id="uni-liste">{items}</div>'
            '<p class="list-empty" data-filter-empty hidden>Keine Universität gefunden. Versuch es mit dem Ort, '
            'z. B. „Mainz“ oder „Berlin“.</p>'
            '<p class="list-foot">SS = Sommersemester, WS = Wintersemester. Klick auf eine Uni zeigt Nachreichfrist, '
            "Kontakt, Postadresse und alle offiziellen Links. Bitte alle Angaben vor dem Absenden auf der offiziellen "
            "Uni-Seite prüfen.</p>")


def los_row(uni, data):
    los = uni["los"]
    official = link_html("Offizielle Seite ↗", los["url"]) if los["url"] else "–"
    return (f'<div class="los-row" id="{esc(uni["id"])}" data-search="{search_text(uni)}">'
            f'<span class="c-name"><a href="{SUBPAGE_PATH}{uni["id"]}/">{esc(display_name(uni))}</a> {higher_tag(uni)}</span>'
            f'<span><span class="mlabel">{esc(data["semester_ws"])}</span>{los_status(los["ws"])}</span>'
            f'<span><span class="mlabel">{esc(data["semester_ss"])}</span>{los_status(los["ss"])}</span>'
            f'<span class="c-link">{official}</span></div>')


def los_list_html(data, listed):
    count = f"{len(listed)} Universitäten · Stand {data['stand']}"
    head = (f'<div class="list-head los" aria-hidden="true"><span>Universität</span><span>{esc(data["semester_ws"])}</span>'
            f'<span>{esc(data["semester_ss"])}</span><span>Offizielle Seite</span></div>')
    rows = "".join(los_row(uni, data) for uni in listed)
    return (f'{list_tools("los-suche", "los-liste", count)}{head}<div id="los-liste">{rows}</div>'
            '<p class="list-empty" data-filter-empty hidden>Keine Universität gefunden. Unis ohne Losverfahren '
            'stehen weiter unten.</p>'
            '<p class="list-foot">Ausgefülltes Quadrat: Zeitraum veröffentlicht. „Auch höhere FS“: Das Losverfahren '
            "gilt dort auch für höhere Fachsemester.</p>")


def ohne_items_html(unis):
    return "".join(f'<li id="{esc(uni["id"])}">{esc(display_name(uni))} – {esc(uni["los"]["ohne"])}</li>'
                   for uni in unis)
