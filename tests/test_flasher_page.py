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


if __name__ == "__main__":
    unittest.main()
