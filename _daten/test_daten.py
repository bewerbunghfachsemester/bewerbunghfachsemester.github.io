"""Prüft die Datenquelle und die erzeugten Blöcke.  Aufruf: python3 -m unittest discover _daten"""

import json
import re
import unittest

from build_pdf import document_html
from build_site import los_rows, start_card, start_rows
from build_unis import sitemap_xml
from common import KNOWN_SCOPES, load_data
from uni_page import page_html, page_url

REQUIRED_FIELDS = ("id", "name", "ss", "ws", "nach", "art", "links", "los")
REQUIRED_LOS_FIELDS = ("ws", "ss", "gilt", "url")


class DatenquelleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.unis = cls.data["unis"]

    def test_jede_uni_hat_alle_pflichtfelder(self):
        for uni in self.unis:
            missing = [field for field in REQUIRED_FIELDS if field not in uni]
            missing_los = [field for field in REQUIRED_LOS_FIELDS if field not in uni.get("los", {})]
            self.assertFalse(missing or missing_los, f"{uni.get('id')}: fehlt {missing + missing_los}")

    def test_ids_sind_eindeutig(self):
        ids = [uni["id"] for uni in self.unis]
        self.assertEqual(len(ids), len(set(ids)))

    def test_links_sind_https_oder_seitenanker(self):
        for uni in self.unis:
            urls = [url for _, url in uni["links"]] + ([uni["los"]["url"]] if uni["los"]["url"] else [])
            for url in urls:
                self.assertTrue(url.startswith("https://") or url.startswith("#"), f"{uni['id']}: {url}")

    def test_gilt_fuer_hat_nur_bekannte_werte(self):
        for uni in self.unis:
            self.assertIn(uni["los"]["gilt"], KNOWN_SCOPES, uni["id"])

    def test_kein_google_sheets_link_mehr(self):
        for uni in self.unis:
            self.assertFalse(any("docs.google.com" in url for _, url in uni["links"]), uni["id"])


class ErzeugteBloeckeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.unis = cls.data["unis"]

    def test_startseiten_tabelle_enthaelt_jede_uni_genau_einmal(self):
        rows = start_rows(self.unis)
        self.assertEqual(rows.count("<tr>"), len(self.unis))

    def test_uni_karte_behaelt_sprungmarke(self):
        card = start_card(self.unis[0])
        self.assertIn(f'id="{self.unis[0]["id"]}"', card)

    def test_sonderzeichen_werden_escaped(self):
        rows = start_rows([{**self.unis[0], "name": "A & B <C>"}])
        self.assertIn("A &amp; B &lt;C&gt;", rows)

    def test_pdf_enthaelt_klickbare_portal_links(self):
        html = document_html(self.data)
        self.assertIn(f'href="{self.unis[0]["links"][0][1]}"', html)

    def test_losverfahren_tabelle_zeigt_beide_semester(self):
        rows = los_rows(self.unis[:1])
        self.assertIn(self.unis[0]["los"]["ws"], rows)
        self.assertIn(self.unis[0]["los"]["ss"], rows)


class UniUnterseitenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.unis = cls.data["unis"]
        cls.pages = {uni["id"]: page_html(uni, cls.data, "", "2026-11-07") for uni in cls.unis}

    def test_jede_uni_hat_kurzname_und_bundesland(self):
        for uni in self.unis:
            self.assertTrue(uni.get("kurz") and uni.get("land"), uni["id"])

    def test_titel_enthaelt_suchbegriff_und_ort(self):
        for uni in self.unis:
            title = re.search(r"<title>(.*?)</title>", self.pages[uni["id"]]).group(1)
            self.assertIn("höheres Fachsemester Medizin", title)
            self.assertIn(uni["kurz"].split(" (")[0], title.replace("&amp;", "&"))

    def test_jede_seite_hat_genau_eine_h1_und_eigenen_canonical(self):
        for uni in self.unis:
            html = self.pages[uni["id"]]
            self.assertEqual(html.count("<h1"), 1, uni["id"])
            self.assertIn(f'<link rel="canonical" href="{page_url(uni)}">', html)

    def test_strukturierte_daten_sind_gueltiges_json(self):
        for uni in self.unis:
            for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.pages[uni["id"]], re.S):
                json.loads(block)

    def test_charite_seite_sagt_dass_wechsel_nicht_moeglich_ist(self):
        self.assertIn("nicht möglich", self.pages["charite-berlin"])
        self.assertNotIn('<ol class="steps">', self.pages["charite-berlin"])

    def test_sitemap_enthaelt_alle_uni_seiten(self):
        sitemap = sitemap_xml(self.unis, "2026-11-07")
        for uni in self.unis:
            self.assertIn(f"<loc>{page_url(uni)}</loc>", sitemap)


if __name__ == "__main__":
    unittest.main()
