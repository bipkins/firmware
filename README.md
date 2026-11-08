# Bipkins™ - Virtual Companion Firmware for ESP32 CYD

An open-source desktop creature platform powered by talkth.ai.

Official public release repository for **Bipkins™** (ESP32-2432S028R "Cheap Yellow Display" / CYD edition).

This repository contains clean, credential-free binaries for first-time installation and seamless upgrades of your Bipkins™ virtual pet device.

---

## 📦 Release Artifacts (v1.3.0)

**What's new in v1.3.0**
- **Your Bipkin looks the same everywhere:** the device now draws the same painted hair, hats, clothes and accessories as talkth.ai. It downloads the art for what your pet is wearing, so new items from the store appear without a firmware update.
- **Looks to keep on the device:** on talkth.ai, choose up to 4 looks to keep on the device ("Keep on device"). Tap the LOOK strip on the device to switch between them, even offline. New items still need talkth.ai.
- **Safer pet switching:** switching pets on talkth.ai no longer risks one pet overwriting another if the device loses power at the wrong moment.
- **Cleaner edges:** sprite edges no longer have a blue fringe.

Upgrading from v1.2.0 keeps your pet, coins, Wi-Fi and pairing. In the Web Flasher, answer **no** when it asks to erase the device. The partition table renames the unused 64 KB crash-dump area at `0x1F0000` to the art cache. Every offset is unchanged, and an **Application Only** upgrade also works, because the firmware accepts the old name.

| File | Offset | Description | Size |
|---|---|---|---|
| `bipkins-cyd-1.3.0-full.bin` | `0x0` | **Full Flash Image**: complete flash image for brand new boards (erases saved pets and Wi-Fi) | ~1.4 MB |
| `bipkins-cyd-1.3.0-app.bin` | `0x10000` | **Application Only**: upgrade image that **preserves existing pet NVS state** | ~1.4 MB |
| `bipkins-cyd-1.3.0-bootloader.bin` | `0x1000` | ESP32 2nd stage bootloader (ESP-IDF 5.5, unchanged from v1.2.0) | ~27 KB |
| `bipkins-cyd-1.3.0-partitions.bin` | `0x8000` | 2 MB partition table (art cache at `0x1F0000`, all offsets unchanged) | ~3 KB |
| `bipkins-cyd-1.3.0-ota_data_initial.bin` | `0xe000` | OTA boot data (blank; boots the app at `0x10000`) | ~8 KB |
| `manifest.json` | - | Web Flasher manifest (build metadata: `releases/1.3.0/manifest.json`) | - |
| `SHA256SUMS` | - | SHA-256 checksums of the v1.3.0 binaries (earlier: `releases/<version>/SHA256SUMS`) | - |

### Checksums
```text
0545b9b3991f721b4aeaa24e16833dce6a70a16be232b862d55d1df798c7e9a4  bipkins-cyd-1.3.0-app.bin
4b6bdecb06a93e3c78e8cb077b61c62e799b94c5af6335fb64f718f4ed0b0be6  bipkins-cyd-1.3.0-bootloader.bin
01b2e17235609d98f69f95cec6228d5a661de5d32c2f59e8acd7d7930e505e55  bipkins-cyd-1.3.0-full.bin
7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f  bipkins-cyd-1.3.0-ota_data_initial.bin
2cdf91f63452a1305bf94210b90bea5a5477c38604fb25a92c26704ba454d8b1  bipkins-cyd-1.3.0-partitions.bin
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
| Plus Jakarta Sans (font, `woff2` + `fonts.css`) | Google Fonts v12 | `docs/vendor/plus-jakarta-sans/` | SIL OFL 1.1 |

Why the files are copied in instead of using `integrity=` on a CDN tag: `install-button.js` is an ES module that loads more modules at run time (`install-dialog-*.js`, the chip-specific `esp32*.js` and `stub_flasher_*.js` chunks). A Subresource Integrity hash only covers the one file named in the tag, not the modules it imports, so SRI on the entry script alone would not stop a swapped chunk. Serving the whole `dist/web/` folder from this repo covers all of them.

`docs/index.html` also carries a Content Security Policy (`script-src 'self'`, `connect-src 'self'`, no other origins), so a script from any other site, or an inline script, is refused by the browser. The page's own code lives in `docs/flasher.js` for that reason; do not put `<script>` code back inline.

The same files are mirrored under `vendor/` and `flasher.js` at the repo root next to the root `index.html`; keep the two copies identical. Publishing GitHub Pages from `/docs` must include `docs/vendor/` and `docs/flasher.js`, or the page will not load.

**Check the vendored files** (no output other than `OK` lines):

```bash
cd docs/vendor && sha256sum -c SHA256SUMS
```

**Update a library** (do this on a branch, never by pointing the page at a CDN):

1. Download the exact release from npm, for example `npm pack esp-web-tools@<new version>` or `bootstrap@<new version>`, into an empty folder, and check the tarball against the `npm view <pkg>@<version> dist.integrity` value.
2. For esp-web-tools copy the whole `package/dist/web/` folder (every `.js` file, because the entry module imports the others) into `docs/vendor/esp-web-tools-<new version>/` together with `LICENSE`. For Bootstrap copy `dist/css/bootstrap.min.css`, `dist/js/bootstrap.bundle.min.js` and `LICENSE`. Do not edit the files. Remove the old version folder.
3. Update the folder names in `docs/index.html` (the `<link>` and `<script>` tags) and the table above. The chunk file names change with every esp-web-tools build; nothing in the HTML refers to them.
4. Regenerate `docs/vendor/SHA256SUMS` (keep its comment header and update the versions and npm integrity values in it), copy `docs/vendor/` to `vendor/`, and copy `docs/index.html` and `docs/flasher.js` to the root.
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
  0x0 bipkins-cyd-1.3.0-full.bin
```

Alternatively, flashing individual components:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x1000  bipkins-cyd-1.3.0-bootloader.bin \
  0x8000  bipkins-cyd-1.3.0-partitions.bin \
  0xe000  bipkins-cyd-1.3.0-ota_data_initial.bin \
  0x10000 bipkins-cyd-1.3.0-app.bin
```

---

### Option B: Upgrading an Existing Pet (Preserves NVS / Pet State)

> 💡 **Important:** To preserve your pet's name, coins, traits, and birthday in NVS memory, flash **only** the application binary to offset `0x10000`. Do **NOT** use `erase_flash` or flash `0x0`.

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x10000 bipkins-cyd-1.3.0-app.bin
```

---

## 📶 Wi-Fi Provisioning & First Setup

This public build contains **no hardcoded Wi-Fi passwords or endpoints**. Wi-Fi is provisioned safely through the USB setup protocol:

1. Connect the CYD board to your computer via USB.
2. Tap the bottom banner on the LCD screen: **"Tap here: WiFi USB setup"**. The screen will indicate a 60-second configuration window.
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

## ⚖️ Legal & Intellectual Property Notice

- **Copyright © 2026 [I-TEAM, INC](https://i-te.am). All rights reserved.**
- **Bipkins™** and **Bipkin™** are common-law trademarks of [I-TEAM, INC](https://i-te.am).
- All original firmware code, artwork, audio waveforms, and lore are protected under U.S. and international copyright law.
