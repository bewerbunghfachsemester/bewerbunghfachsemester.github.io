"""Inhalt einer Uni-Unterseite (/hoeheres-fachsemester/<id>/) aus den Daten einer Universität."""

import json

from common import (
    PDF_URL, SCOPE_ALSO_HIGHER, SCOPE_FIRST_ONLY, SCOPE_NONE, contact_html, esc, link_html,
)
from layout import THEME_COLOR, footer, head_assets, topbar

SITE_URL = "https://www.bewerbungsrenner.com"
SECTION_PATH = "/hoeheres-fachsemester/"
NOT_POSSIBLE = "nicht möglich"
NO_DEADLINE_VALUES = ("–", "")

TITLE = "Bewerbung höheres Fachsemester Medizin {kurz}"
DESCRIPTION = ("{name}: Bewerbung ins höhere Fachsemester Medizin – Fristen, Nachreichfrist, Kontakt, "
               "Losverfahren und offizielle Links. Kostenlos, Stand {stand}.")
LPA_ANSWER = ("In der Regel das Landesprüfungsamt deines Geburtsbundeslandes – nicht das Bundesland, in dem die "
              "Universität liegt. Die genaue Zuständigkeit solltest du vor dem Antrag beim Landesprüfungsamt prüfen.")


def page_url(uni):
    return f"{SITE_URL}{SECTION_PATH}{uni['id']}/"


def deadlines_sentence(uni):
    if uni["ss"] == NOT_POSSIBLE:
        return "Laut Universität ist ein Wechsel ins höhere Fachsemester Medizin hier nicht möglich."
    return f"Zum Sommersemester: {uni['ss']} · zum Wintersemester: {uni['ws']}."


def application_route(uni):
    art = uni["art"]
    if art.startswith("über"):
        return "Die Bewerbung läuft über die FAU Erlangen-Nürnberg."
    if "Online" in art and "Post" in art:
        return "Du bewirbst dich online über das Bewerbungsportal und schickst danach Antrag und Unterlagen per Post."
    if "online" in art.lower():
        return "Die Bewerbung läuft online über das Bewerbungsportal der Universität."
    if art == "Post":
        return "Die Bewerbung läuft per Post."
    return "Wie du dich bewirbst, steht auf der Bewerbungsseite der Universität."


def late_documents(uni):
    value = uni["nach"]
    if value == "keine":
        return "Eine Nachreichfrist gibt es nicht – alle Unterlagen müssen bis zum Bewerbungsschluss vorliegen."
    if value in NO_DEADLINE_VALUES:
        return "Eine Nachreichfrist ist nicht bekannt – reiche am besten alle Unterlagen bis zum Bewerbungsschluss ein."
    return f"Nachreichfrist für fehlende Nachweise: {value}."


def lottery_text(uni):
    kurz, scope = uni["kurz"], uni["los"]["gilt"]
    if scope == SCOPE_ALSO_HIGHER:
        return (f"{kurz} verlost freie Plätze ausdrücklich auch in höheren Fachsemestern. Dafür brauchst du in der "
                "Regel eine Anrechnung bzw. Einstufung, für das 1. klinische Semester das Physikum.")
    if scope == SCOPE_FIRST_ONLY:
        return (f"Das Losverfahren in {kurz} betrifft nur das 1. Fachsemester. Für einen Wechsel ins höhere "
                "Fachsemester zählt hier allein die reguläre Bewerbung.")
    if scope == SCOPE_NONE:
        return f"In {kurz} gibt es nach aktuellem Stand kein eigenes Losverfahren für Medizin."
    return (f"Ob das Losverfahren in {kurz} auch höhere Fachsemester umfasst, sagt die Universität nicht "
            "ausdrücklich. Meist betrifft es nur das 1. Fachsemester.")


def faq_items(uni):
    first = (deadlines_sentence(uni) if uni["ss"] == NOT_POSSIBLE
             else f"{deadlines_sentence(uni)} Maßgeblich ist immer die offizielle Seite der Universität.")
    return (
        (f"Wann ist die Bewerbungsfrist für das höhere Fachsemester Medizin in {uni['kurz']}?", first),
        (f"Gibt es in {uni['kurz']} ein Losverfahren für höhere Fachsemester?", lottery_text(uni)),
        ("Welches Landesprüfungsamt ist für die Anrechnung zuständig?", LPA_ANSWER),
    )


def structured_data(uni, stand_iso):
    title = TITLE.format(kurz=uni["kurz"])
    webpage = {
        "@context": "https://schema.org", "@type": "WebPage", "name": title, "url": page_url(uni),
        "inLanguage": "de-DE", "dateModified": stand_iso, "isAccessibleForFree": True,
        "about": {"@type": "CollegeOrUniversity", "name": uni["name"]},
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Start", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": uni["kurz"], "item": page_url(uni)},
        ],
    }
    faq = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": question,
                        "acceptedAnswer": {"@type": "Answer", "text": answer}} for question, answer in faq_items(uni)],
    }
    return "\n".join(f'<script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>'
                     for block in (webpage, breadcrumb, faq))


def head_html(uni, data, stand_iso):
    title = esc(TITLE.format(kurz=uni["kurz"]))
    description = esc(DESCRIPTION.format(name=uni["name"], stand=data["stand"]))
    url = page_url(uni)
    return f"""<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="article">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="bewerbungsrenner.com">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="{THEME_COLOR}">
{head_assets()}
{structured_data(uni, stand_iso)}
</head>"""


def fact(label, value_html):
    return f"<dt>{label}</dt><dd>{value_html}</dd>"


def facts_card(uni):
    rows = [fact("Bewerbung SS", esc(uni["ss"])), fact("Bewerbung WS", esc(uni["ws"])),
            fact("Nachreichfrist", esc(uni["nach"])), fact("Art", esc(uni["art"])),
            fact("Kontakt", contact_html(uni)), fact("Bundesland", esc(uni["land"]))]
    if uni.get("post"):
        rows.append(fact("Postadresse", esc(uni["post"])))
    note = f'<p class="uni-note">{esc(uni["hinweis"])}</p>' if uni.get("hinweis") else ""
    return f'<div class="uni-card"><dl class="uni-facts">{"".join(rows)}</dl>{note}</div>'


def steps_html(uni):
    if uni["ss"] == NOT_POSSIBLE:
        return f'<p class="body">{esc(deadlines_sentence(uni))} Prüfe Alternativen wie einen Studienplatztausch an anderen Universitäten oder die übrigen Unis in der <a href="/#liste">Uni-Liste</a>.</p>'
    portal = link_html("Bewerbungsportal", uni["links"][0][1])
    steps = (
        "Lass deine bisherigen Studienleistungen anrechnen. Wer aus dem Ausland oder einem anderen Studiengang "
        "kommt, braucht meist eine Anrechnung bzw. Einstufung durch das Landesprüfungsamt; bei einem Wechsel im "
        "gleichen Studiengang innerhalb Deutschlands reicht oft der Nachweis des bisherigen Studiums.",
        esc(deadlines_sentence(uni)) + " Die Fristen sind in der Regel Ausschlussfristen.",
        esc(application_route(uni)) + f" Direkt zum {portal}.",
        esc(late_documents(uni)),
        "Prüfe alle Angaben vor dem Absenden auf der offiziellen Seite der Universität.",
    )
    return '<ol class="steps">' + "".join(f"<li>{step}</li>" for step in steps) + "</ol>"


def lottery_section(uni):
    los = uni["los"]
    link = f'<p class="uni-links">{link_html("Zur Losverfahren-Seite", los["url"], "↗")}</p>' if los["url"] else ""
    facts = fact("WiSe", esc(los["ws"])) + fact("SoSe", esc(los["ss"])) + fact("Gilt für", esc(los["gilt"]))
    return (f'<p class="body">{esc(lottery_text(uni))}</p>'
            f'<div class="uni-card" style="margin-top:16px"><dl class="uni-facts">{facts}</dl>{link}</div>')


def related_section(uni, unis):
    neighbours = [other for other in unis if other["land"] == uni["land"] and other["id"] != uni["id"]]
    items = "".join(f'<li><a href="{SECTION_PATH}{other["id"]}/">Höheres Fachsemester Medizin {esc(other["kurz"])}</a></li>'
                    for other in neighbours)
    same_state = (f"<h3>Weitere Universitäten in {esc(uni['land'])}</h3><ul class=\"plain\">{items}</ul>"
                  if neighbours else "")
    return (f'{same_state}<p class="note" style="margin-top:18px">Alle Universitäten mit Fristen und Links findest du '
            f'in der <a href="/#liste">Uni-Liste</a> – auch <a href="{PDF_URL}" download>als PDF zum Herunterladen</a>.</p>')


def faq_section(uni):
    return "".join(f'<details class="faq"><summary>{esc(question)}</summary><p>{esc(answer)}</p></details>'
                   for question, answer in faq_items(uni))


def section(number, anchor, heading, body):
    return f'<section id="{anchor}"><h2><span class="num">{number:02d}</span>{heading}</h2>{body}</section>'


def page_html(uni, data, stand_iso):
    links = "".join(f"<li>{link_html(label, url, '↗' if url.startswith('http') else '↑')}</li>"
                    for label, url in uni["links"])
    intro = (f"Alles für deinen Wechsel ins höhere Fachsemester Humanmedizin an der Universität: Fristen, "
             f"Nachreichfrist, Bewerbungsweg, Kontakt und Losverfahren – geprüft und mit direkten Links zu den "
             f"offiziellen Seiten.")
    body = (
        section(1, "fristen", "Fristen &amp; Eckdaten", facts_card(uni))
        + section(2, "bewerbung", f"So bewirbst du dich in {esc(uni['kurz'])}", steps_html(uni))
        + section(3, "losverfahren", f"Losverfahren in {esc(uni['kurz'])}", lottery_section(uni))
        + section(4, "links", "Offizielle Links", f'<ul class="plain">{links}</ul>')
        + section(5, "weitere", "Weitere Universitäten", related_section(uni, data["unis"]))
        + section(6, "faq", "Häufige Fragen", faq_section(uni))
    )
    return f"""<!doctype html>
<html lang="de">
{head_html(uni, data, stand_iso)}
<body>
{topbar()}
<header class="hero"><div class="wrap">
<nav class="breadcrumb" aria-label="Brotkrumen"><a href="/">Start</a> › <a href="/#liste">Uni-Liste</a> › {esc(uni['kurz'])}</nav>
<p class="eyebrow">Höheres Fachsemester Medizin · {esc(uni['land'])}</p>
<h1 class="compact">Bewerbung höheres Fachsemester Medizin: {esc(uni['name'])}</h1>
<div class="hero-lead"><p class="big">{intro}</p>
<div class="hero-side"><p>{esc(deadlines_sentence(uni))}</p>
<div class="hero-actions"><a class="cta" href="{esc(uni['links'][0][1])}" target="_blank" rel="noopener nofollow">Zur Bewerbungsseite →</a><span class="stand">Stand: {esc(data['stand'])}</span></div></div></div>
</div></header>
<main class="wrap">{body}
<p class="note">Alle Angaben ohne Gewähr. Universitäten ändern Fristen, Portale und Anforderungen – bitte vor der Bewerbung die verlinkte offizielle Seite prüfen.</p>
</main>
{footer()}
</body>
</html>
"""
