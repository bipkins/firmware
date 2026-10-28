# Bipkins™ - Virtual Companion Firmware for ESP32 CYD

An open-source desktop creature platform powered by talkth.ai.

Official public release repository for **Bipkins™** (ESP32-2432S028R "Cheap Yellow Display" / CYD edition).

This repository contains clean, credential-free binaries for first-time installation and seamless upgrades of your Bipkins™ virtual pet device.

---

## 📦 Release Artifacts (v1.2.0)

**What's new in v1.2.0**
- **Cloud sync:** your Bipkin stays in step with talkth.ai. Care, coins and pet changes sync both ways, and the website shows when the device was last online.
- **Sleep hours:** your pet sleeps through the night. The default is 21:00–07:00 in your local time, and you can change it on talkth.ai. If you wake your pet during sleep hours, it goes back to sleep after 10 minutes idle.
- **Re-pairing keeps your pet:** pairing again (or adopting an egg) keeps the same pet and species. A device that is forgotten on talkth.ai and paired again no longer drops back to "unlinked".
- **Day-scale needs:** hunger and joy fall over hours rather than minutes, and more slowly while the pet sleeps.
- **New build system:** the firmware is now built with ESP-IDF 5.5. That is why the bootloader and the boot data part (`ota_data_initial`, which replaces `boot_app0`) are new in this release. The partition table has not changed.

Upgrading from v1.1.0 keeps your pet, coins, Wi-Fi and pairing, whether you flash only the **Application** image or all four parts without erasing. In the Web Flasher, answer **no** when it asks to erase the device.

| File | Offset | Description | Size |
|---|---|---|---|
| `bipkins-cyd-1.2.0-full.bin` | `0x0` | **Full Flash Image**: complete flash image for brand new boards (erases saved pets and Wi-Fi) | ~1.4 MB |
| `bipkins-cyd-1.2.0-app.bin` | `0x10000` | **Application Only**: upgrade image that **preserves existing pet NVS state** | ~1.3 MB |
| `bipkins-cyd-1.2.0-bootloader.bin` | `0x1000` | ESP32 2nd stage bootloader (ESP-IDF 5.5) | ~27 KB |
| `bipkins-cyd-1.2.0-partitions.bin` | `0x8000` | Custom 2 MB partition table (unchanged since v1.0.0) | ~3 KB |
| `bipkins-cyd-1.2.0-ota_data_initial.bin` | `0xe000` | OTA boot data (blank; boots the app at `0x10000`) | ~8 KB |
| `manifest.json` | - | Web Flasher manifest (build metadata: `releases/1.2.0/manifest.json`) | - |
| `SHA256SUMS` | - | SHA-256 checksums of the v1.2.0 binaries (earlier: `releases/<version>/SHA256SUMS`) | - |

### Checksums
```text
144bd474119cdb657695a3b9fc051addd06af4fd473b1dacffdf4317fab3e144  bipkins-cyd-1.2.0-app.bin
4b6bdecb06a93e3c78e8cb077b61c62e799b94c5af6335fb64f718f4ed0b0be6  bipkins-cyd-1.2.0-bootloader.bin
c4ca0267ffc7daa5af66c3d5b2942b55ad68a29351dba4bc98a99c4d60489bdf  bipkins-cyd-1.2.0-full.bin
7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f  bipkins-cyd-1.2.0-ota_data_initial.bin
b04ba681eca2feb3b65cb564a6e7961c3caf9beecf21445b0fc2ad087c53a550  bipkins-cyd-1.2.0-partitions.bin
```

---

## ⚡ In-Browser Web Flasher (No Installation Required)

If you are using Chrome, Edge, or Opera on desktop, you can flash your Bipkin directly from the web without installing Python or `esptool`:

1. Open the **[Bipkins™ Web Flasher](docs/index.html)** (hosted directly via GitHub Pages under `/docs`).
2. Connect your CYD ESP32 board to your computer via USB.
3. Select your hardware model (e.g. `ESP32-2432S028R`), click **Connect & Install Bipkins™**, and choose your serial port.
4. Follow the on-screen installer instructions.

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
  0x0 bipkins-cyd-1.2.0-full.bin
```

Alternatively, flashing individual components:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x1000  bipkins-cyd-1.2.0-bootloader.bin \
  0x8000  bipkins-cyd-1.2.0-partitions.bin \
  0xe000  bipkins-cyd-1.2.0-ota_data_initial.bin \
  0x10000 bipkins-cyd-1.2.0-app.bin
```

---

### Option B: Upgrading an Existing Pet (Preserves NVS / Pet State)

> 💡 **Important:** To preserve your pet's name, coins, traits, and birthday in NVS memory, flash **only** the application binary to offset `0x10000`. Do **NOT** use `erase_flash` or flash `0x0`.

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x10000 bipkins-cyd-1.2.0-app.bin
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
