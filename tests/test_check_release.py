"""Tests for scripts/check_release.py. Run: python3 -m unittest discover -s tests -v"""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_release as cr  # noqa: E402

ROLES = {  # role -> (flash offset, served file name stem)
    "bootloader": (0x1000, "bootloader"),
    "partitions": (0x8000, "partitions"),
    "ota_data_initial": (0xE000, "ota_data_initial"),
    "app": (0x10000, "bipkins_cyd"),
}
PENDING = {"status": "pending", "needs": "owner on-device test"}
LEGACY = {"status": "published-legacy", "note": "published before the gate"}


def approved(**kw):
    rec = {"status": "approved", "date": "2026-11-09", "by": "owner", "tested": "flashed on a CYD"}
    rec.update(kw)
    return rec


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else data.encode())


def make_repo(root, releases, served):
    """releases: {version: publication}. served: version the flasher points at."""
    for version, pub in releases.items():
        lines = []
        for role, (_, stem) in ROLES.items():
            name = f"bipkins-cyd-{version}-{role}.bin"
            data = f"{version}-{role}".encode()
            write(root / name, data)
            write(root / "builds" / f"{stem}_v{version}.bin", data)
            write(root / "docs" / "builds" / f"{stem}_v{version}.bin", data)
            lines.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
        write(root / "releases" / version / "SHA256SUMS", "\n".join(lines) + "\n")
        write(root / "releases" / version / "manifest.json",
              json.dumps({"version": version, "publication": pub}, indent=2) + "\n")

    def manifest(prefix):
        parts = [{"path": f"{prefix}builds/{stem}_v{served}.bin", "offset": off}
                 for _, (off, stem) in ROLES.items()]
        return json.dumps({"version": served, "builds": [{"chipFamily": "ESP32", "parts": parts}]})
    write(root / "manifest.json", manifest(""))
    write(root / "docs" / "manifests" / "cyd.json", manifest("../"))


def run(root, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = cr.main(["--root", str(root), *args])
    return rc, out.getvalue()


class CheckReleaseTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_approved_passes(self):
        make_repo(self.root, {"1.3.0": LEGACY, "1.4.1": approved()}, "1.4.1")
        rc, out = run(self.root)
        self.assertEqual(rc, 0, out)
        self.assertIn("OK: safe to publish", out)

    def test_pending_fails(self):
        make_repo(self.root, {"1.3.0": LEGACY, "1.4.1": PENDING}, "1.4.1")
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("1.4.1 is not approved", out)
        self.assertIn("pending", out)

    def test_checksum_mismatch_in_release_fails(self):
        make_repo(self.root, {"1.4.1": approved()}, "1.4.1")
        write(self.root / "bipkins-cyd-1.4.1-app.bin", b"tampered")
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("bipkins-cyd-1.4.1-app.bin does not match", out)

    def test_missing_listed_file_fails(self):
        make_repo(self.root, {"1.3.0": LEGACY, "1.4.1": approved()}, "1.4.1")
        (self.root / "bipkins-cyd-1.3.0-partitions.bin").unlink()
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("1.3.0-partitions.bin is listed in SHA256SUMS but the file is missing", out)

    def test_served_binary_differs_from_release_fails(self):
        make_repo(self.root, {"1.4.1": approved()}, "1.4.1")
        write(self.root / "docs" / "builds" / "bipkins_cyd_v1.4.1.bin", b"other build")
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("docs/manifests/cyd.json", out)
        self.assertIn("does not match bipkins-cyd-1.4.1-app.bin", out)

    def test_served_binary_missing_fails(self):
        make_repo(self.root, {"1.4.1": approved()}, "1.4.1")
        (self.root / "builds" / "bootloader_v1.4.1.bin").unlink()
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("is served but the file is missing", out)

    def test_served_version_older_than_newest_approved_fails(self):
        make_repo(self.root, {"1.3.0": LEGACY, "1.4.1": approved()}, "1.3.0")
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("newest approved release is 1.4.1", out)

    def test_serving_last_published_while_newer_is_pending_passes(self):
        make_repo(self.root, {"1.3.0": LEGACY, "1.4.1": PENDING}, "1.3.0")
        rc, out = run(self.root)
        self.assertEqual(rc, 0, out)

    def test_two_served_manifests_must_agree(self):
        make_repo(self.root, {"1.3.0": LEGACY, "1.4.1": approved()}, "1.4.1")
        m = json.loads((self.root / "manifest.json").read_text())
        m["version"] = "1.3.0"
        (self.root / "manifest.json").write_text(json.dumps(m))
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("different versions", out)

    def test_legacy_accepted_for_old_versions_only(self):
        make_repo(self.root, {"1.3.0": LEGACY}, "1.3.0")
        self.assertEqual(run(self.root)[0], 0)
        other = Path(tempfile.mkdtemp(dir=self.root))
        make_repo(other, {"1.4.1": LEGACY}, "1.4.1")
        rc, out = run(other)
        self.assertEqual(rc, 1)
        self.assertIn("only allowed for versions up to 1.3.0", out)

    def test_old_free_text_is_legacy_only_for_old_versions(self):
        text = "BLOCKED: independent exposure/security review"
        make_repo(self.root, {"1.2.0": text}, "1.2.0")
        self.assertEqual(run(self.root)[0], 0)
        other = Path(tempfile.mkdtemp(dir=self.root))
        make_repo(other, {"1.4.1": text}, "1.4.1")
        rc, out = run(other)
        self.assertEqual(rc, 1)
        self.assertIn("free text, not an approval record", out)

    def test_incomplete_approval_record_fails(self):
        make_repo(self.root, {"1.4.1": approved(tested="")}, "1.4.1")
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("missing: tested", out)

    def test_bad_approval_date_fails(self):
        make_repo(self.root, {"1.4.1": approved(date="yesterday")}, "1.4.1")
        rc, out = run(self.root)
        self.assertEqual(rc, 1)
        self.assertIn("not YYYY-MM-DD", out)

    def test_approve_turns_pending_into_pass(self):
        make_repo(self.root, {"1.3.0": LEGACY, "1.4.1": PENDING}, "1.4.1")
        self.assertEqual(run(self.root)[0], 1)
        rc, out = run(self.root, "--approve", "1.4.1", "--tested", "flashed on a CYD, paired")
        self.assertEqual(rc, 0, out)
        rec = json.loads((self.root / "releases/1.4.1/manifest.json").read_text())["publication"]
        self.assertEqual(rec["status"], "approved")
        self.assertEqual(rec["by"], "owner")
        self.assertEqual(rec["tested"], "flashed on a CYD, paired")
        self.assertRegex(rec["date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(run(self.root)[0], 0)

    def test_approve_requires_tested_text(self):
        make_repo(self.root, {"1.4.1": PENDING}, "1.4.1")
        rc, out = run(self.root, "--approve", "1.4.1")
        self.assertEqual(rc, 2)
        self.assertIn("--tested", out)
        self.assertEqual(json.loads((self.root / "releases/1.4.1/manifest.json").read_text())["publication"], PENDING)

    def test_approve_unknown_version(self):
        make_repo(self.root, {"1.4.1": PENDING}, "1.4.1")
        rc, out = run(self.root, "--approve", "9.9.9", "--tested", "x")
        self.assertEqual(rc, 2)
        self.assertIn("no release 9.9.9", out)

    def test_approve_refuses_legacy_release(self):
        make_repo(self.root, {"1.3.0": LEGACY}, "1.3.0")
        rc, out = run(self.root, "--approve", "1.3.0", "--tested", "x")
        self.assertEqual(rc, 2)
        self.assertIn("already settled", out)


if __name__ == "__main__":
    unittest.main()
