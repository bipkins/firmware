# Bipkins™ - Virtual Companion Firmware for ESP32 CYD

An open-source desktop creature platform powered by talkth.ai.

Official public release repository for **Bipkins™** (ESP32-2432S028R "Cheap Yellow Display" / CYD edition).

This repository contains clean, credential-free binaries for first-time installation and seamless upgrades of your Bipkins™ virtual pet device.

---

## 📦 Release Artifacts (v1.4.3)

**What's new in v1.4.3**
- **All 20 games reviewed and polished:** every game now has a clear goal and gives feedback on every tap.
- **No free points for doing nothing:** a game no longer scores while you leave it alone.
- **Fixed repeating cues:** the picks in Trick Flags and Whack a Sprout no longer follow a pattern you can learn.
- **Smoothie Studio shows the recipe and the fruit** you need, so you can tell what to do.
- **Input stops at the end of a game:** nothing moves or scores after the end screen.
- **A result card after every game:** your score, misses and the coins you earned.
- **The website learns at once** when a game starts and when it ends.

**Also new since v1.4.1 (v1.4.2)**
- **Pairing shows up quickly:** after you pair on the website, the device now shows it is paired within about 10 seconds. While a pairing code is on the screen (including the code card on the home screen) the device checks every 10 seconds instead of waiting.
- **Restoring a saved pet brings back its exact look:** restoring a saved pet from the website now brings back its exact look, whether it has hatched, and its care levels (food, fun, rest and so on), even on a board whose memory was erased. This needs the talkth.ai server update, which is already live.

**Also new since v1.4.0 (v1.4.1)**
- **Safer clock:** the device only trusts the time it gets from the talkth server over a verified secure connection, and an internet time check may only back up a time the server has already confirmed (for up to 72 hours).
- **Safer USB:** the released firmware refuses debug commands over the USB cable. The USB setup page still works as before.
- **Pairing works in more cases and says when it is offline:** the device understands pairing codes however they are spaced, says so on screen when there is no Wi-Fi while waiting to pair, and backs off politely when the server asks it to slow down.

**Also new since v1.3.0 (v1.4.0)**
- **Feeding from talkth.ai feeds right away:** pressing Feed on the website now feeds your Bipkin directly, with its eating animation, instead of placing a pellet you had to drag on the touchscreen.
- **Faster replies to the website:** while the Mirror page is open, the device checks in every 5 seconds, so care, pet switches and other website actions arrive in about 3–7 seconds instead of up to 15.
- **It tells you why:** when your Bipkin can't do something (too full, asleep, needs a rest), the website shows the reason.
- **Care shows up sooner:** care done on the device reaches the website within a moment.
- **Safer setup hotspot:** each device now makes its own random hotspot password, shown on its screen, instead of one that could be worked out from the device's name.
- **Unguessable device IDs for new boards:** a newly set up device gets an ID nobody can predict. Devices that are already paired keep their ID.
- **The full store on the device:** every hat, pair of sunglasses, halo and other wearable item now shows on every species (133 pieces of art), and the forest pet's eyes are cleaner.

Upgrading from v1.3.0, v1.4.0, v1.4.1 or v1.4.2 keeps your pet, coins, Wi-Fi and pairing. In the Web Flasher, answer **no** when it asks to erase the device. The bootloader, partition table and boot data are byte-identical to v1.3.0, v1.4.0, v1.4.1 and v1.4.2; only the application changes, so an **Application Only** upgrade also works.

| File | Offset | Description | Size |
|---|---|---|---|
| `bipkins-cyd-1.4.3-full.bin` | `0x0` | **Full Flash Image**: complete flash image for brand new boards (erases saved pets and Wi-Fi) | ~1.4 MB |
| `bipkins-cyd-1.4.3-app.bin` | `0x10000` | **Application Only**: upgrade image that **preserves existing pet NVS state** | ~1.4 MB |
| `bipkins-cyd-1.4.3-bootloader.bin` | `0x1000` | ESP32 2nd stage bootloader (ESP-IDF 5.5, unchanged since v1.2.0) | ~27 KB |
| `bipkins-cyd-1.4.3-partitions.bin` | `0x8000` | 2 MB partition table (unchanged from v1.3.0) | ~3 KB |
| `bipkins-cyd-1.4.3-ota_data_initial.bin` | `0xe000` | OTA boot data (blank; boots the app at `0x10000`) | ~8 KB |
| `manifest.json` | - | Web Flasher manifest (build metadata: `releases/1.4.3/manifest.json`) | - |
| `SHA256SUMS` | - | SHA-256 checksums of the v1.4.3 binaries (earlier: `releases/<version>/SHA256SUMS`) | - |

### Checksums
```text
49a9cbcd24d7afbda3ab861f52320c9a02bec97e106941cddb68e42e359c869c  bipkins-cyd-1.4.3-app.bin
4b6bdecb06a93e3c78e8cb077b61c62e799b94c5af6335fb64f718f4ed0b0be6  bipkins-cyd-1.4.3-bootloader.bin
61246c430dfa6478b15b8290ecb796efd4a9f60ff5ca75ae8509cdc27d6dab54  bipkins-cyd-1.4.3-full.bin
7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f  bipkins-cyd-1.4.3-ota_data_initial.bin
2cdf91f63452a1305bf94210b90bea5a5477c38604fb25a92c26704ba454d8b1  bipkins-cyd-1.4.3-partitions.bin
```

---

## ⚡ In-Browser Web Flasher (No Installation Required)

If you are using Chrome, Edge, or Opera on desktop, you can flash your Bipkin directly from the web without installing Python or `esptool`:

1. Open the **[Bipkins™ Web Flasher](docs/index.html)** (hosted directly via GitHub Pages under `/docs`).
2. Connect your CYD ESP32 board to your computer via USB.
3. Select your hardware model (e.g. `ESP32-2432S028R`), click **Connect & Install Bipkins™**, and choose your serial port.
4. Follow the on-screen installer instructions.

### Third-party scripts

The flasher page runs with Web Serial access, so it loads **no code from another website**. Everything it needs is committed in this repo, pinned to an exact version, and served from the same origin:

| What | Version | Where | Licence |
|---|---|---|---|
| [esp-web-tools](https://github.com/esphome/esp-web-tools) (the install button) | 10.4.0 | `docs/vendor/esp-web-tools-10.4.0/` | Apache-2.0 |
| [Bootstrap](https://getbootstrap.com) CSS and JS | 5.3.3 | `docs/vendor/bootstrap-5.3.3/` | MIT |

**Look.** The page uses the talkth.ai palette and type (the `:root` colours, the system sans-serif stack, Georgia headings, 9 px buttons, bordered 13 px cards) from `docs/flasher.css`, loaded after Bootstrap. talkth.ai is light-only and loads no web fonts, so this page loads none either (there is no font to vendor). The talkth.ai logo and favicon are `docs/brand.svg` and `docs/favicon.svg`. To restyle, change the variables at the top of `docs/flasher.css`; keep it in step with talkth-web `static/style.css`.

**Release line.** The page shows `Release: v<version>` and nothing else about the release. `flasher.js` reads `version` from the manifest of the selected hardware target (`docs/manifests/*.json`), so the line follows the manifest and needs no edit per release. Do not put release notes in the page; they stay in this README and `releases/<version>/`.

Why the files are copied in instead of using `integrity=` on a CDN tag: `install-button.js` is an ES module that loads more modules at run time (`install-dialog-*.js`, the chip-specific `esp32*.js` and `stub_flasher_*.js` chunks). A Subresource Integrity hash only covers the one file named in the tag, not the modules it imports, so SRI on the entry script alone would not stop a swapped chunk. Serving the whole `dist/web/` folder from this repo covers all of them.

`docs/index.html` also carries a Content Security Policy (`script-src 'self'`, `connect-src 'self'`, no other origins), so a script from any other site, or an inline script, is refused by the browser. The page's own code lives in `docs/flasher.js` for that reason; do not put `<script>` code back inline.

The same files are mirrored under `vendor/`, `flasher.js`, `flasher.css`, `brand.svg`, `favicon.svg`, `setup.html` and `index.html` at the repo root; keep the two copies identical (`tests/test_flasher_page.py` checks this). Publishing GitHub Pages from `/docs` must include `docs/vendor/`, `docs/flasher.js` and `docs/flasher.css`, or the page will not load.

**Check the vendored files** (no output other than `OK` lines):

```bash
cd docs/vendor && sha256sum -c SHA256SUMS
```

**Update a library** (do this on a branch, never by pointing the page at a CDN):

1. Download the exact release from npm, for example `npm pack esp-web-tools@<new version>` or `bootstrap@<new version>`, into an empty folder, and check the tarball against the `npm view <pkg>@<version> dist.integrity` value.
2. For esp-web-tools copy the whole `package/dist/web/` folder (every `.js` file, because the entry module imports the others) into `docs/vendor/esp-web-tools-<new version>/` together with `LICENSE`. For Bootstrap copy `dist/css/bootstrap.min.css`, `dist/js/bootstrap.bundle.min.js` and `LICENSE`. Do not edit the files. Remove the old version folder.
3. Update the folder names in `docs/index.html` (the `<link>` and `<script>` tags) and the table above. The chunk file names change with every esp-web-tools build; nothing in the HTML refers to them.
4. Regenerate `docs/vendor/SHA256SUMS` (keep its comment header and update the versions and npm integrity values in it), copy `docs/vendor/` to `vendor/`, and copy `docs/index.html`, `docs/flasher.js` and `docs/flasher.css` to the root.
5. Serve `docs/` locally (`cd docs && python3 -m http.server 8196`), open the page in Chrome or Edge with the console open, and confirm there are no errors and no Content Security Policy messages. Click **Connect & Install** and confirm the port picker opens (stop there unless you intend to flash a test board).

---

## 🚀 Manual CLI Flashing Instructions (`esptool.py`)

### Prerequisites
- Python 3 with `esptool`:
  ```bash
  pip install esptool
  ```
- A USB data cable connected to the CYD ESP32 board (identifies as `/dev/ttyUSB0` or `COMx`).

---

### Option A: Fresh Install on a New Board (Full Flash)

> ⚠️ **Notice:** This writes starting at address `0x0`. Use this for first-time installation on a blank board.

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x0 bipkins-cyd-1.4.3-full.bin
```

Alternatively, flashing individual components:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x1000  bipkins-cyd-1.4.3-bootloader.bin \
  0x8000  bipkins-cyd-1.4.3-partitions.bin \
  0xe000  bipkins-cyd-1.4.3-ota_data_initial.bin \
  0x10000 bipkins-cyd-1.4.3-app.bin
```

---

### Option B: Upgrading an Existing Pet (Preserves NVS / Pet State)

> 💡 **Important:** To preserve your pet's name, coins, traits, and birthday in NVS memory, flash **only** the application binary to offset `0x10000`. Do **NOT** use `erase_flash` or flash `0x0`.

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x10000 bipkins-cyd-1.4.3-app.bin
```

---

## 📶 Wi-Fi Provisioning & First Setup

This public build contains **no hardcoded Wi-Fi passwords or endpoints**. Wi-Fi is provisioned safely through the USB setup protocol:

1. Connect the CYD board to your computer via USB.
2. On the LCD screen tap **SET UP WI-FI**, then **USB Web Flasher Setup**. This opens a 60-second configuration window.
3. Open a Web Serial terminal (or the talkth.ai USB setup page) at 115200 baud, or send the command:
   ```text
   NETWORK <SSID> <PASSWORD>
   ```
4. The board will reply:
   ```text
   [NETWORK] Stored SSID=<SSID>; restart to connect
   ```
5. Power-cycle or reboot the device. The Bipkin will connect to your local Wi-Fi, verify public time via TLS, and start normal pet care routines!

---

## 🛠️ Publishing a release (maintainers)

The web flasher is published to GitHub Pages by hand, so nothing stops a half-tested build from going live except this checklist. `scripts/check_release.py` (Python 3, no packages needed) is the gate: it fails unless every checksum matches, both flasher manifests (`manifest.json` and `docs/manifests/cyd-2432s028r.json`) point at the newest release that has been approved, and that release carries an approval record.

1. **Build** the release with the release script in talkth-pets (`scripts/release_firmware.py`). It writes the binaries, `releases/<version>/SHA256SUMS` and `releases/<version>/manifest.json` with `"publication": {"status": "pending", ...}`. Update the flasher manifests and `builds/` / `docs/builds/` to the new version.
2. **Test on a device**: flash the build to a real board, check pairing and the care actions, and (for an upgrade) that the pet's state survived.
3. **Record the approval**:
   ```bash
   python3 scripts/check_release.py --approve <version> --tested "what you checked on the device"
   ```
   This writes `{"status": "approved", "date": ..., "by": "owner", "tested": ...}` into `releases/<version>/manifest.json` and then runs the check.
4. **Check**: `python3 scripts/check_release.py` must end with `OK: safe to publish`. Any `FAIL:` line says in plain English what to fix. Do not publish while it fails.
5. **Commit and merge** the approval together with the release.
6. **Publish** `main` to GitHub Pages.
7. **Confirm it is live**: `curl -s https://bipkins.github.io/firmware/manifests/cyd-2432s028r.json` must show `"version": "<version>"`.

The `publication` field of a release manifest is one of `pending`, `approved`, `superseded` (a build that was never published on its own) or `published-legacy` (1.1.0 to 1.3.0, published before the gate existed; not accepted for newer versions). Tests for the check: `python3 -m unittest discover -s tests`.

Release 1.0.0 is no longer in this repository: nothing served or documented it, and its `SHA256SUMS` did not match the files. It remains in git history.

---

## ⚖️ Legal & Intellectual Property Notice

- **Copyright © 2026 [I-TEAM, INC](https://i-te.am). All rights reserved.**
- **Bipkins™** and **Bipkin™** are common-law trademarks of [I-TEAM, INC](https://i-te.am).
- All original firmware code, artwork, audio waveforms, and lore are protected under U.S. and international copyright law.
