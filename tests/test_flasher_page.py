"""Checks on the flasher page itself. Run: python3 -m unittest discover -s tests -v"""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRRORED = ["index.html", "flasher.js", "flasher.css", "flash_support.js", "brand.svg", "favicon.svg", "setup.html"]


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

    def test_board_is_named_exactly_and_other_versions_are_not_supported_yet(self):
        html = read("docs/index.html")
        self.assertIn("ESP32-2432S028R (single USB port, resistive touch)", html)
        self.assertRegex(html, r"two USB ports, USB-C plus micro-USB, or capacitive touch\) are not supported yet")
        self.assertRegex(html, r"cannot tell board versions apart")  # nothing pretends to detect the variant
        self.assertNotRegex(html, r"S028_2USB|S028C|Dual USB-C|Coming Soon")
        readme = read("README.md")
        self.assertIn("ESP32-2432S028R (single USB port, resistive touch)", readme)
        self.assertIn("are not supported yet", readme)

    def test_cable_wording_does_not_assert_one_connector(self):
        for name in ("docs/index.html", "README.md"):
            text = read(name)
            self.assertNotRegex(text, r"USB-C data cable", name)
            self.assertIn("most of these boards use micro-USB; some use USB-C", text, name)

    def test_phone_gate_is_wired_without_inline_script_or_email_capture(self):
        html = read("docs/index.html")
        self.assertIn('id="flashGate"', html)
        self.assertLess(html.index("flash_support.js"), html.index('src="flasher.js"'))
        self.assertNotRegex(html + read("docs/flash_support.js"), r"type=\"email\"|<input[^>]*email|mailto:")
        self.assertIn("showGateIfNeeded", read("docs/flasher.js"))


@unittest.skipUnless(shutil.which("node"), "node is needed to run the detection logic")
class FlashSupportLogic(unittest.TestCase):
    """docs/flash_support.js is a plain script that Node can load, so its detection runs here for real."""

    SCRIPT = r"""
const fs = require(process.argv[1] + '/docs/flash_support.js');
const UA = {
  android: 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/130.0 Mobile Safari/537.36',
  iphone: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1',
  ipad: 'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1',
  firefox: 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
  safari: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.5 Safari/605.1.15',
  chrome: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36',
};
const out = {
  chrome: fs.flashSupport({ userAgent: UA.chrome, serial: {} }),
  android: fs.flashSupport({ userAgent: UA.android }),
  iphone: fs.flashSupport({ userAgent: UA.iphone }),
  ipad: fs.flashSupport({ userAgent: UA.ipad }),
  ipadDesktopMode: fs.flashSupport({ userAgent: UA.safari, platform: 'MacIntel', maxTouchPoints: 5 }),
  uaDataMobile: fs.flashSupport({ userAgent: UA.firefox, userAgentData: { mobile: true } }),
  firefox: fs.flashSupport({ userAgent: UA.firefox, platform: 'Linux x86_64', maxTouchPoints: 0 }),
  safariMac: fs.flashSupport({ userAgent: UA.safari, platform: 'MacIntel', maxTouchPoints: 0 }),
};
(async () => {
  let written = null;
  out.copyApi = await fs.copyText('u', { clipboard: { writeText: async (t) => { written = t; } } }, {});
  out.copyApiText = written;
  const calls = [];
  const doc = { body: { appendChild() {} }, createElement() { return { style: {}, setAttribute() {}, select() {}, remove() {} }; }, execCommand(c) { calls.push(c); return true; } };
  out.copyFallback = await fs.copyText('u', {}, doc);
  out.fallbackCalls = calls;
  out.copyFails = await fs.copyText('u', {}, { body: { appendChild() { throw new Error('x'); } }, createElement() { return { style: {}, setAttribute() {} }; } });
  console.log(JSON.stringify(out));
})();
"""

    def test_detection_and_copy(self):
        out = json.loads(subprocess.run(["node", "-e", self.SCRIPT, str(ROOT)], capture_output=True, text=True,
                                        check=True).stdout)
        self.assertEqual("ok", out["chrome"])
        for key in ("android", "iphone", "ipad", "ipadDesktopMode", "uaDataMobile"):
            self.assertEqual("phone", out[key], key)
        for key in ("firefox", "safariMac"):
            self.assertEqual("browser", out[key], key)
        self.assertTrue(out["copyApi"])
        self.assertEqual("u", out["copyApiText"])
        self.assertTrue(out["copyFallback"])
        self.assertEqual(["copy"], out["fallbackCalls"])
        self.assertFalse(out["copyFails"])


if __name__ == "__main__":
    unittest.main()
