"""Erzeugt das Vorschaubild für WhatsApp, LinkedIn & Co. (og-image.png, 1200 × 630 Pixel).

Aufruf (im Projektordner):  python3 _daten/build_og.py
Baut eine HTML-Fassung im Design der Website aus unis.json und fotografiert sie mit Google Chrome (headless).
Danach bei LinkedIn (linkedin.com/post-inspector) bzw. Facebook (Sharing-Debugger) den Cache neu laden lassen.
"""

import logging
import subprocess

from blocks import MONTHS, TIMELINE_TRACKS, year_percent
from build_pdf import CHROME_BINARY, FONTS
from common import BUILD_DIR, ROOT_DIR, esc, load_data

LOGGER = logging.getLogger("build_og")

WIDTH, HEIGHT = 1200, 630
OG_PATH = ROOT_DIR / "og-image.png"
HTML_PATH = BUILD_DIR / "og-image.html"
RENDER_WAIT_MS = 8000

BRAND = "bewerbungsrenner"
BRAND_TLD = ".com"
EYEBROW = "Kostenlos · unabhängig · 2026"
HEADLINE = ("Kostenlose Bewerbung", "höheres Fachsemester", "Medizin 2026")
FIGURE_LABEL = "Uni-Liste · Stand {stand}"
FIGURE_UNIT = "Unis"
FIGURE_TEXT = "Fristen, Portale, Unterlagen und\u00a0Losverfahren"

BRAND_MARK = ('<svg width="34" height="34" viewBox="0 0 24 24" aria-hidden="true">'
              '<rect width="24" height="24" fill="#111111"></rect>'
              '<rect x="4" y="15" width="16" height="1.6" fill="#ffffff"></rect>'
              '<rect x="10" y="8" width="7" height="5.4" fill="#ff5b14"></rect></svg>')

STYLES = """
:root{--ink:#111;--paper:#fff;--text:#33332f;--muted:#5f5f58;--grid:#e2e2dd;--ext:#cfcfc9;--acc:#ff5b14;
--sans:"Archivo",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,monospace}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1200px;height:630px;overflow:hidden}
body{display:flex;flex-direction:column;background:var(--paper);color:var(--ink);font-family:var(--sans)}
.top{display:flex;align-items:center;justify-content:space-between;height:84px;padding:0 56px;
border-bottom:1px solid var(--ink)}
.brand{display:flex;align-items:center;gap:14px;font-size:27px;font-weight:700;letter-spacing:-.01em}
.brand span span{font-weight:400;color:var(--muted)}
.mono{font-family:var(--mono);font-size:14px;letter-spacing:.1em;text-transform:uppercase}
.main{flex:1;display:flex;flex-direction:column;justify-content:space-between;padding:34px 56px 30px}
.hero{display:flex;align-items:flex-end;justify-content:space-between;gap:40px}
h1{font-size:92px;font-stretch:72%;font-weight:760;line-height:.92;letter-spacing:-.015em}
h1 span{display:block;padding-bottom:.04em}
.figure{flex:0 0 250px;padding-top:12px;border-top:2px solid var(--ink)}
.figure .mono{font-size:12px;letter-spacing:.06em}
.figure .num{display:flex;align-items:flex-end;gap:10px;margin-top:4px}
.figure .digits{font-size:132px;font-weight:740;font-stretch:70%;line-height:.86}
.figure .unit{padding-bottom:10px;font-size:24px;font-weight:600}
.figure .text{margin-top:10px;font-size:16px;line-height:1.35;color:var(--text)}
.chart{display:grid;grid-template-columns:232px 1fr;border-top:1px solid var(--ink)}
.labels p,.plot>div{display:flex;align-items:center;height:27px}
.labels p{font-family:var(--mono);font-size:13px}
.plot{background-image:linear-gradient(to right,var(--grid) 1px,transparent 1px);background-size:calc(100% / 12) 100%}
.plot>.months{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));font-family:var(--mono);font-size:12px;
color:var(--muted)}
.months span{padding-left:7px}
.bars{position:relative}
.bar{position:absolute;top:7px;bottom:7px;background:var(--ink)}
.bar.ext{background:var(--ext)}
.bar.los{background:var(--acc)}
.ticker{display:flex;align-items:center;gap:36px;height:58px;padding-left:56px;overflow:hidden;
background:var(--ink);color:var(--paper);font-family:var(--mono);font-size:15px;white-space:nowrap}
.ticker p{display:flex;align-items:center;gap:14px}
.ticker p::before{content:"";width:8px;height:8px;background:var(--acc)}
.ticker span{color:#a9a9a3}
"""


def bar_html(start, end, kind):
    left = year_percent(*start)
    width = year_percent(*end) - left
    css_class = f"bar {kind}".strip()
    return f'<span class="{css_class}" style="left:{left:.2f}%;width:{width:.2f}%"></span>'


def chart_html():
    """Das Bewerbungsjahr der Startseite, ohne Heute-Markierung, damit das Bild nicht veraltet."""
    labels = '<p></p>' + "".join(f"<p>{esc(label)}</p>" for label, _ in TIMELINE_TRACKS)
    months = "".join(f"<span>{month}</span>" for month in MONTHS)
    tracks = "".join(
        '<div class="bars">' + "".join(bar_html(start, end, kind) for start, end, kind in bars) + "</div>"
        for _, bars in TIMELINE_TRACKS
    )
    return (f'<div class="chart"><div class="labels">{labels}</div>'
            f'<div class="plot"><div class="months">{months}</div>{tracks}</div></div>')


def ticker_html(unis):
    items = "".join(f'<p>{esc(uni["name"])}<span>SS {esc(uni["ss"])} · WS {esc(uni["ws"])}</span></p>'
                    for uni in unis[:4])
    return f'<div class="ticker">{items}</div>'


def og_html(data):
    headline = "".join(f"<span>{esc(line)}</span>" for line in HEADLINE)
    figure = (f'<div class="figure"><p class="mono">{esc(FIGURE_LABEL.format(stand=data["stand"]))}</p>'
              f'<div class="num"><span class="digits">{len(data["unis"])}</span>'
              f'<span class="unit">{esc(FIGURE_UNIT)}</span></div>'
              f'<p class="text">{esc(FIGURE_TEXT)}</p></div>')
    return (
        f'<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{esc(" ".join(HEADLINE))}</title>'
        f'<link rel="stylesheet" href="{FONTS}"><style>{STYLES}</style></head><body>'
        f'<div class="top"><p class="brand">{BRAND_MARK}<span>{esc(BRAND)}<span>{esc(BRAND_TLD)}</span></span></p>'
        f'<p class="mono">{esc(EYEBROW)}</p></div>'
        f'<div class="main"><div class="hero"><h1>{headline}</h1>{figure}</div>{chart_html()}</div>'
        f"{ticker_html(data['unis'])}</body></html>"
    )


def screenshot(html_path, png_path):
    if not CHROME_BINARY.exists():
        raise FileNotFoundError(f"Google Chrome nicht gefunden: {CHROME_BINARY}")
    command = [
        str(CHROME_BINARY), "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--window-size={WIDTH},{HEIGHT}", "--force-device-scale-factor=1",
        f"--virtual-time-budget={RENDER_WAIT_MS}", f"--screenshot={png_path}", html_path.resolve().as_uri(),
    ]
    subprocess.run(command, check=True, capture_output=True, timeout=120)


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    data = load_data()
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(og_html(data), encoding="utf-8")
    screenshot(HTML_PATH, OG_PATH)
    LOGGER.info("Vorschaubild erstellt: %s (%d Universitäten)", OG_PATH, len(data["unis"]))


if __name__ == "__main__":
    main()
