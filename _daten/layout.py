"""Gemeinsame Seitenteile im neuen Design: Head-Ressourcen, Navigation, Footer."""

ASSET_VERSION = "2026-11-07"
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..800"
             "&amp;family=IBM+Plex+Mono:wght@400;500&amp;display=swap")
STYLESHEETS = ("base", "components", "content", "lists", "motion")
THEME_COLOR = "#111111"
CONTACT_MAIL = "bewerbung.h.fachsemester@gmail.com"

NAV_ITEMS = (("/", "Uni-Liste", "liste"), ("/losverfahren/", "Losverfahren", "losverfahren"),
             ("/medizin-restplaetze/", "Restplätze", "restplaetze"))

BRAND_MARK = (
    '<svg class="brand-mark" width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">'
    '<rect width="24" height="24" fill="#111111"></rect>'
    '<rect x="4" y="15" width="16" height="1.6" fill="#ffffff"></rect>'
    '<rect class="window" x="10" y="8" width="7" height="5.4"></rect></svg>'
)


def head_assets():
    """Schriften, Stylesheets und Skript für jede Seite."""
    links = "\n".join(
        f'    <link rel="stylesheet" href="/assets/{name}.css?v={ASSET_VERSION}" />' for name in STYLESHEETS
    )
    return (
        '    <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
        '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
        f'    <link rel="stylesheet" href="{FONTS_URL}" />\n'
        f"{links}\n"
        f'    <script src="/assets/site.js?v={ASSET_VERSION}" defer></script>'
    )


def topbar(active=""):
    """Kopfzeile mit Marke und Hauptnavigation; `active` markiert die aktuelle Seite."""
    current = ' aria-current="page"'
    links = "".join(
        f'<a href="{href}"{current if key == active else ""}>{label}</a>'
        for href, label, key in NAV_ITEMS
    )
    return (
        '<div class="topbar"><div class="wrap">'
        f'<a class="brand" href="/">{BRAND_MARK}<span class="brand-name">bewerbungsrenner<span>.com</span></span></a>'
        f'<nav aria-label="Hauptmenü">{links}</nav></div></div>'
    )


def footer():
    links = "".join(f'<a href="{href}">{label}</a>' for href, label, _ in NAV_ITEMS)
    return (
        '<footer><div class="wrap"><h2>Fragen?</h2>'
        "<p>Bei Fragen, Korrekturen oder Hinweisen zu veralteten Links:</p>"
        f'<a class="mail" href="mailto:{CONTACT_MAIL}">{CONTACT_MAIL}</a>'
        '<div class="legal"><span>© 2026 bewerbungsrenner.com · Kostenlose Uni-Liste höheres Fachsemester Medizin</span>'
        f'<nav aria-label="Fußzeile">{links}</nav></div></div></footer>'
    )
