#!/usr/bin/env python3
"""Pre-publish gate for the Bipkins web flasher (bipkins #5).

Run this from anywhere before you publish main to GitHub Pages:

    python3 scripts/check_release.py

It exits 0 and prints "OK" only when it is safe to publish. Otherwise it exits 1
and prints one plain-English "FAIL" line per problem. It checks that:

  1. every file listed in every releases/<version>/SHA256SUMS exists and matches;
  2. every binary the served flasher manifests point at exists and matches the
     SHA256SUMS of the version that manifest claims;
  3. the served version is the newest release that has been approved for
     publication (releases/<version>/manifest.json -> "publication");
  4. that release's "publication" field is a real approval record.

Record your approval after testing a build on a device:

    python3 scripts/check_release.py --approve 1.4.1 --tested "flashed on a CYD, paired, fed the pet"

The "publication" field of a release manifest is one of:

    {"status": "pending", "needs": "owner on-device test"}
    {"status": "approved", "date": "YYYY-MM-DD", "by": "owner", "tested": "..."}
    {"status": "published-legacy", "note": "..."}   only for versions up to LEGACY_MAX
    {"status": "superseded", "by": "<newer version>"}

Standard library only.
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

# Versions up to this one were published before the gate existed. For them (and
# only them) "published-legacy" and the old free-text "BLOCKED: ..." string are
# accepted. Anything newer needs a real approval record.
LEGACY_MAX = (1, 3, 0)

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
FILE_VERSION = re.compile(r"_v(\d+\.\d+\.\d+)\.bin$")

# Flash offset -> names of the release file that holds that part, in order of preference.
OFFSET_ROLES = {
    0x0: ("full",),
    0x1000: ("bootloader",),
    0x8000: ("partitions",),
    0xE000: ("ota_data_initial", "boot_app0"),
    0x10000: ("app",),
}

ROOT_DEFAULT = Path(__file__).resolve().parent.parent


def vkey(version):
    return tuple(int(x) for x in version.split("."))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path, problems):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        problems.append(f"{path} is missing.")
    except (ValueError, OSError) as e:
        problems.append(f"{path} cannot be read as JSON ({e}).")
    return None


def parse_sums(path, problems):
    """Return {file name: sha256} from a SHA256SUMS file, or None if unreadable."""
    sums = {}
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        problems.append(f"{path} cannot be read ({e}).")
        return None
    for n, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([0-9a-fA-F]{64}) [ *](.+)$", line)
        if not m:
            problems.append(f"{path} line {n} is not in 'hash  filename' form.")
            continue
        sums[m.group(2)] = m.group(1).lower()
    return sums


def rel(root, path):
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return str(path)


def find_releases(root):
    out = {}
    rdir = root / "releases"
    if rdir.is_dir():
        for d in sorted(rdir.iterdir()):
            if d.is_dir() and SEMVER.match(d.name):
                out[d.name] = d
    return out


def check_sums(root, releases, problems, notes):
    """Check 1. Returns {version: {name: sha256}} for versions whose sums parsed."""
    all_sums = {}
    for version in sorted(releases, key=vkey):
        sums_path = releases[version] / "SHA256SUMS"
        if not sums_path.exists():
            problems.append(f"Release {version} has no SHA256SUMS file ({rel(root, sums_path)}).")
            continue
        sums = parse_sums(sums_path, problems)
        if sums is None:
            continue
        if not sums:
            problems.append(f"Release {version}: {rel(root, sums_path)} lists no files.")
            continue
        all_sums[version] = sums
        bad = 0
        for name, want in sorted(sums.items()):
            f = root / name
            if not f.is_file():
                problems.append(f"Release {version}: {name} is listed in SHA256SUMS but the file is missing.")
                bad += 1
            elif sha256(f) != want:
                problems.append(f"Release {version}: {name} does not match its SHA256SUMS entry "
                                f"(file is {sha256(f)[:12]}..., list says {want[:12]}...).")
                bad += 1
        if not bad:
            notes.append(f"Release {version}: all {len(sums)} files match SHA256SUMS.")
    # The top-level SHA256SUMS is a convenience copy of the newest release's sums.
    top = root / "SHA256SUMS"
    if top.exists():
        sums = parse_sums(top, problems)
        for name, want in sorted((sums or {}).items()):
            f = root / name
            if not f.is_file():
                problems.append(f"Top-level SHA256SUMS lists {name} but the file is missing.")
            elif sha256(f) != want:
                problems.append(f"Top-level SHA256SUMS: {name} does not match the file.")
    return all_sums


def served_manifests(root):
    found = []
    top = root / "manifest.json"
    if top.exists():
        found.append(top)
    mdir = root / "docs" / "manifests"
    if mdir.is_dir():
        found.extend(sorted(mdir.glob("*.json")))
    return found


def check_served(root, path, all_sums, problems, notes):
    """Check 2 for one served manifest. Returns its version string or None."""
    label = rel(root, path)
    m = read_json(path, problems)
    if m is None:
        return None
    version = m.get("version")
    if not isinstance(version, str) or not SEMVER.match(version):
        problems.append(f"{label} has no valid 'version' (found {version!r}).")
        return None
    sums = all_sums.get(version)
    if sums is None:
        problems.append(f"{label} says version {version}, but release {version} has no usable SHA256SUMS.")
    bad = 0
    count = 0
    for build in m.get("builds", []):
        for part in build.get("parts", []):
            count += 1
            ppath = part.get("path", "")
            offset = part.get("offset")
            f = (path.parent / ppath).resolve()
            if not f.is_file():
                problems.append(f"{label}: {ppath} is served but the file is missing.")
                bad += 1
                continue
            fv = FILE_VERSION.search(ppath)
            if fv and fv.group(1) != version:
                problems.append(f"{label}: {ppath} is a v{fv.group(1)} file but the manifest says {version}.")
                bad += 1
            roles = OFFSET_ROLES.get(offset)
            if roles is None:
                problems.append(f"{label}: {ppath} is flashed at unknown offset {offset!r}; "
                                f"this check does not know which release file it should match.")
                bad += 1
                continue
            if sums is None:
                bad += 1
                continue
            names = [f"bipkins-cyd-{version}-{r}.bin" for r in roles]
            names = [n for n in names if n in sums]
            if not names:
                problems.append(f"{label}: release {version} has no SHA256SUMS entry for {ppath} "
                                f"(expected {' or '.join(f'bipkins-cyd-{version}-{r}.bin' for r in roles)}).")
                bad += 1
                continue
            actual = sha256(f)
            if actual != sums[names[0]]:
                problems.append(f"{label}: {ppath} does not match {names[0]} in release {version} "
                                f"(file is {actual[:12]}..., SHA256SUMS says {sums[names[0]][:12]}...).")
                bad += 1
    if count == 0:
        problems.append(f"{label} lists no files to flash.")
    elif not bad:
        notes.append(f"{label}: version {version}, all {count} files exist and match SHA256SUMS.")
    return version


def classify(version, pub):
    """Return (kind, message). kind: 'approved' | 'legacy' | 'pending' | 'superseded' | 'invalid'."""
    legacy_ok = vkey(version) <= LEGACY_MAX
    if isinstance(pub, str):
        if legacy_ok:
            return "legacy", "old free-text publication field (legacy)"
        return "invalid", ("its 'publication' field is free text, not an approval record. "
                           "Run: python3 scripts/check_release.py --approve " + version + ' --tested "..."')
    if not isinstance(pub, dict):
        return "invalid", "it has no 'publication' record."
    status = pub.get("status")
    if status == "approved":
        missing = [k for k in ("date", "by", "tested") if not str(pub.get(k, "")).strip()]
        if missing:
            return "invalid", "its approval record is missing: " + ", ".join(missing) + "."
        try:
            datetime.date.fromisoformat(pub["date"])
        except (ValueError, TypeError):
            return "invalid", f"its approval date {pub['date']!r} is not YYYY-MM-DD."
        return "approved", f"approved {pub['date']} by {pub['by']}"
    if status == "published-legacy":
        if legacy_ok:
            return "legacy", "published before the gate was enforced"
        return "invalid", (f"'published-legacy' is only allowed for versions up to "
                           f"{'.'.join(map(str, LEGACY_MAX))}.")
    if status == "pending":
        return "pending", "approval is pending (" + str(pub.get("needs", "no reason given")) + ")"
    if status == "superseded":
        return "superseded", "superseded by " + str(pub.get("by", "?"))
    return "invalid", f"unknown publication status {status!r}."


def check_publication(root, releases, served_versions, problems, notes):
    """Checks 3 and 4."""
    kinds = {}
    for version in sorted(releases, key=vkey):
        mp = releases[version] / "manifest.json"
        if not mp.exists():
            kinds[version] = ("missing", "it has no manifest.json")
            continue
        sub = []
        data = read_json(mp, sub)
        if data is None:
            kinds[version] = ("invalid", "its manifest.json cannot be read")
            problems.extend(sub)
            continue
        kinds[version] = classify(version, data.get("publication"))
    publishable = [v for v, (k, _) in kinds.items() if k in ("approved", "legacy")]
    newest_ok = max(publishable, key=vkey) if publishable else None
    for version in sorted(set(served_versions)):
        kind, msg = kinds.get(version, ("missing", f"there is no releases/{version}/ folder"))
        if kind not in ("approved", "legacy"):
            problems.append(f"The flasher serves {version}, but {version} is not approved for publication: {msg}")
        elif newest_ok is not None and version != newest_ok:
            problems.append(f"The flasher serves {version}, but the newest approved release is {newest_ok}.")
        else:
            notes.append(f"Release {version}: {msg}.")
    if len(set(served_versions)) > 1:
        problems.append("The served manifests point at different versions: "
                        + ", ".join(sorted(set(served_versions), key=vkey)) + ".")


def run_check(root):
    problems, notes = [], []
    releases = find_releases(root)
    if not releases:
        problems.append("No releases found under releases/.")
    all_sums = check_sums(root, releases, problems, notes)
    served = served_manifests(root)
    if len(served) < 2:
        problems.append("Expected both served manifests (manifest.json and docs/manifests/*.json) "
                        f"but found {len(served)}.")
    versions = [v for v in (check_served(root, p, all_sums, problems, notes) for p in served) if v]
    check_publication(root, releases, versions, problems, notes)
    return problems, notes


def approve(root, version, tested, by):
    mp = root / "releases" / version / "manifest.json"
    if not SEMVER.match(version) or not mp.exists():
        print(f"FAIL: there is no release {version} (looked for {rel(root, mp)}).")
        return 2
    if not tested.strip():
        print('FAIL: say what you tested, e.g. --tested "flashed on a CYD, paired, fed the pet".')
        return 2
    data = json.loads(mp.read_text(encoding="utf-8"))
    kind, msg = classify(version, data.get("publication"))
    if kind in ("approved", "legacy", "superseded"):
        print(f"FAIL: release {version} is already settled: {msg}. Edit the manifest by hand if you really mean to change it.")
        return 2
    data["publication"] = {"status": "approved", "date": datetime.date.today().isoformat(),
                           "by": by, "tested": tested.strip()}
    mp.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Recorded approval of {version} in {rel(root, mp)}:")
    print("  " + json.dumps(data["publication"]))
    print()
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check that the repo is safe to publish to GitHub Pages.")
    ap.add_argument("--root", default=str(ROOT_DEFAULT), help="repo root (default: this repo)")
    ap.add_argument("--approve", metavar="VERSION", help="record on-device approval of a release, then run the check")
    ap.add_argument("--tested", default="", help="what you checked on a device (required with --approve)")
    ap.add_argument("--by", default="owner", help="who approved (default: owner)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if args.approve:
        rc = approve(root, args.approve, args.tested, args.by)
        if rc is not None:
            return rc
    problems, notes = run_check(root)
    for n in notes:
        print("ok:   " + n)
    for p in problems:
        print("FAIL: " + p)
    if problems:
        print(f"\nNOT SAFE TO PUBLISH: {len(problems)} problem(s) above.")
        return 1
    print("\nOK: safe to publish. The flasher serves an approved release and every file matches its checksum.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
