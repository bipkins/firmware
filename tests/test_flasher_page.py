"""Checks on the flasher page itself. Run: python3 -m unittest discover -s tests -v"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRRORED = ["index.html", "flasher.js", "flasher.css", "brand.svg", "favicon.svg", "setup.html"]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


class FlasherPage(unittest.TestCase):
    def test_root_copy_matches_docs(self):
        for name in MIRRORED:
            self.assertEqual(read(name), read("docs/" + name), f"{name} differs between docs/ and the root")

    def test_release_line_is_version_only(self):
        html = read("docs/index.html")
        self.assertNotRegex(html, r"Release:\s*v\d", "version is hard-coded in the page; flasher.js must fill it in")
        js = read("docs/flasher.js")
        self.assertIn("'Release: v' + version", js)
        self.assertNotRegex(js, r"\.json\(\)\)\.(?!version\b)\w+", "only the version may be read from the manifest")

    def test_no_external_origins_and_csp_kept(self):
        for name in ("docs/index.html", "docs/flasher.css", "docs/setup.html"):
            self.assertNotRegex(read(name), r"(?:https?:)?//(?!talkth\.ai|i-te\.am|www\.w3\.org)[\w.-]+\.\w+/",
                                f"{name} loads from another origin")
        self.assertIn("script-src 'self'", read("docs/index.html"))

    def test_page_has_no_inline_script_and_uses_talkth_palette(self):
        html = read("docs/index.html")
        self.assertIsNone(re.search(r"<script(?![^>]*\bsrc=)", html), "inline <script> is blocked by the CSP")
        css = read("docs/flasher.css")
        for token in ("--green: #426a51", "--cream: #f8f6ef", "--paper: #fffdf7", "Georgia"):
            self.assertIn(token, css)

    def test_no_page_sends_dev_only_serial_commands(self):
        # Release firmware refuses these (talkth-pets docs/PUBLIC_FIRMWARE.md); the working path is NETWORK.
        for name in ("docs/index.html", "docs/flasher.js", "docs/setup.html"):
            self.assertNotRegex(read(name), r"SET_WIFI|WIFI_CONFIG|BRIDGE_TIME|TIME_SYNC", name)
        self.assertIn("NETWORK ", read("docs/setup.html"))

    def test_no_unbacked_claims_or_removed_controls(self):
        html = read("docs/index.html")
        for text in ("100% private", "Air-Gapped", "verified Bipkins", "Push Wi-Fi", "Clock Sync"):
            self.assertNotIn(text, html)
        self.assertIn('href="setup.html"', html)
        for ident in ("wifiSsid", "wifiPass", "btnPushWifi", "btnUsbBridge"):
            self.assertNotIn(ident, html)

    def test_type_scale_matches_talkth(self):
        css = read("docs/flasher.css")
        html = read("docs/index.html")
        self.assertIn(".flasher-card h4 { font-size: 21px; font-weight: 400;", css)  # step titles: regular, like talkth section h2
        self.assertIn(".option-card h5 { font-size: 17px; font-weight: 500;", css)  # card titles: like talkth h3
        self.assertIn("font-size: 11px; font-weight: 650", css)  # buttons: like .primary-button
        self.assertIn("font-weight: 750", css)  # badge: like .gallery-card-badge
        self.assertNotRegex(html, r"<h[1-6][^>]*class=\"[^\"]*\bfw-(bold|bolder|semibold)", "Bootstrap bold on a heading")
        self.assertNotRegex(html, r"\bfs-[1-6]\b|\bdisplay-\d|class=\"(?:[^\"]* )?lead[ \"]", "Bootstrap type-scale classes leak a different size")


    def test_both_pages_have_age_line_and_legal_links(self):
        for name in ("docs/index.html", "docs/setup.html"):
            html = read(name)
            self.assertIn("For ages 13 and up.", html, f"{name} lacks the age statement")
            for label, url in (("Terms", "https://talkth.ai/terms"),
                               ("Privacy", "https://talkth.ai/privacy"),
                               ("Safety", "https://talkth.ai/safety")):
                self.assertRegex(html, rf'<a href="{re.escape(url)}"[^>]*>{label}</a>', f"{name} lacks the {label} link")


if __name__ == "__main__":
    unittest.main()
