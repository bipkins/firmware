# Bipkins™ - Virtual Companion Firmware for ESP32 CYD

An open-source desktop creature platform powered by talkth.ai.

Official public release repository for **Bipkins™** (ESP32-2432S028R "Cheap Yellow Display" / CYD edition).

This repository contains clean, credential-free binaries for first-time installation and seamless upgrades of your Bipkins™ virtual pet device.

---

## 📦 Release Artifacts (v1.4.1)

**What's new in v1.4.1**
- **Safer clock:** the device now only trusts the time it gets from the talkth server over a verified secure connection. A cable or a look-alike network can no longer set it. An internet time check may back up a time the server has already confirmed, for up to 72 hours.
- **Safer USB:** the released firmware refuses debug commands over the USB cable (for example saving Wi-Fi without touching the screen, setting the clock or faking a pairing code). The USB setup page still works as before.
- **Pairing works in more cases:** the device now understands pairing codes from the server however they are spaced.
- **Pairing tells you when it is offline:** if there is no Wi-Fi while the device is waiting to pair, the screen says so instead of showing a code that cannot work. The pairing screen updates as soon as a new code arrives, and the device backs off politely when the server asks it to slow down.

**Also new since v1.3.0 (v1.4.0)**
- **Feeding from talkth.ai feeds right away:** pressing Feed on the website now feeds your Bipkin directly, with its eating animation, instead of placing a pellet you had to drag on the touchscreen.
- **Faster replies to the website:** while the Mirror page is open, the device checks in every 5 seconds, so care, pet switches and other website actions arrive in about 3–7 seconds instead of up to 15.
- **It tells you why:** when your Bipkin can't do something (too full, asleep, needs a rest), the website shows the reason.
- **Care shows up sooner:** care done on the device reaches the website within a moment.
- **Safer setup hotspot:** each device now makes its own random hotspot password, shown on its screen, instead of one that could be worked out from the device's name.
- **Unguessable device IDs for new boards:** a newly set up device gets an ID nobody can predict. Devices that are already paired keep their ID.
- **The full store on the device:** every hat, pair of sunglasses, halo and other wearable item now shows on every species (133 pieces of art), and the forest pet's eyes are cleaner.

Upgrading from v1.3.0 or v1.4.0 keeps your pet, coins, Wi-Fi and pairing. In the Web Flasher, answer **no** when it asks to erase the device. The bootloader, partition table and boot data are byte-identical to v1.3.0 and v1.4.0; only the application changes, so an **Application Only** upgrade also works.

| File | Offset | Description | Size |
|---|---|---|---|
| `bipkins-cyd-1.4.1-full.bin` | `0x0` | **Full Flash Image**: complete flash image for brand new boards (erases saved pets and Wi-Fi) | ~1.4 MB |
| `bipkins-cyd-1.4.1-app.bin` | `0x10000` | **Application Only**: upgrade image that **preserves existing pet NVS state** | ~1.4 MB |
| `bipkins-cyd-1.4.1-bootloader.bin` | `0x1000` | ESP32 2nd stage bootloader (ESP-IDF 5.5, unchanged since v1.2.0) | ~27 KB |
| `bipkins-cyd-1.4.1-partitions.bin` | `0x8000` | 2 MB partition table (unchanged from v1.3.0) | ~3 KB |
| `bipkins-cyd-1.4.1-ota_data_initial.bin` | `0xe000` | OTA boot data (blank; boots the app at `0x10000`) | ~8 KB |
| `manifest.json` | - | Web Flasher manifest (build metadata: `releases/1.4.1/manifest.json`) | - |
| `SHA256SUMS` | - | SHA-256 checksums of the v1.4.1 binaries (earlier: `releases/<version>/SHA256SUMS`) | - |

### Checksums
```text
32d12b68d1668bcdeccfd456906fd9e0ec2680903cd4b72317349560ebcfc5fc  bipkins-cyd-1.4.1-app.bin
4b6bdecb06a93e3c78e8cb077b61c62e799b94c5af6335fb64f718f4ed0b0be6  bipkins-cyd-1.4.1-bootloader.bin
0570c9897ed83514c1022d231f82b4b3468424978a9f6091f034a29325f00f2e  bipkins-cyd-1.4.1-full.bin
7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f  bipkins-cyd-1.4.1-ota_data_initial.bin
2cdf91f63452a1305bf94210b90bea5a5477c38604fb25a92c26704ba454d8b1  bipkins-cyd-1.4.1-partitions.bin
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
  0x0 bipkins-cyd-1.4.1-full.bin
```

Alternatively, flashing individual components:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x1000  bipkins-cyd-1.4.1-bootloader.bin \
  0x8000  bipkins-cyd-1.4.1-partitions.bin \
  0xe000  bipkins-cyd-1.4.1-ota_data_initial.bin \
  0x10000 bipkins-cyd-1.4.1-app.bin
```

---

### Option B: Upgrading an Existing Pet (Preserves NVS / Pet State)

> 💡 **Important:** To preserve your pet's name, coins, traits, and birthday in NVS memory, flash **only** the application binary to offset `0x10000`. Do **NOT** use `erase_flash` or flash `0x0`.

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x10000 bipkins-cyd-1.4.1-app.bin
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
