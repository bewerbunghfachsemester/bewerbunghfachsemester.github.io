"""Prüft das Vorschaubild für WhatsApp, LinkedIn & Co.  Aufruf: python3 -m unittest discover _daten"""

import struct
import unittest

from blocks import TIMELINE_TRACKS
from build_og import HEIGHT, OG_PATH, WIDTH, og_html
from common import load_data

WHATSAPP_MAX_BYTES = 300 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(path):
    """Breite und Höhe aus dem IHDR-Kopf einer PNG-Datei."""
    header = path.read_bytes()[:24]
    if not header.startswith(PNG_SIGNATURE):
        raise ValueError(f"keine PNG-Datei: {path}")
    return struct.unpack(">II", header[16:24])


class VorschaubildHtmlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.html = og_html(cls.data)

    def test_nennt_die_anzahl_der_unis_aus_den_daten(self):
        self.assertIn(f">{len(self.data['unis'])}<", self.html)

    def test_nennt_den_stand_aus_den_daten(self):
        self.assertIn(self.data["stand"], self.html)

    def test_zeigt_alle_spuren_des_bewerbungsjahrs(self):
        for label, _ in TIMELINE_TRACKS:
            self.assertIn(label, self.html)


class VorschaubildDateiTest(unittest.TestCase):
    def test_hat_das_format_1200_mal_630(self):
        self.assertEqual(png_size(OG_PATH), (WIDTH, HEIGHT))

    def test_ist_klein_genug_fuer_whatsapp(self):
        self.assertLess(OG_PATH.stat().st_size, WHATSAPP_MAX_BYTES)


if __name__ == "__main__":
    unittest.main()
