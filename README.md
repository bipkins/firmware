# Bipkins CYD Firmware Release

Official public release repository for **Bipkins** (ESP32-2432S028R "Cheap Yellow Display" / CYD edition).

This repository contains clean, credential-free binaries for first-time installation and seamless upgrades of your Bipkin virtual pet device.

---

## 📦 Release Artifacts (v1.0.0)

| File | Offset | Description | Size |
|---|---|---|---|
| `bipkins-cyd-1.0.0-full.bin` | `0x0` | **Full Flash Image**: Complete flash image for brand new boards | ~1.4 MB |
| `bipkins-cyd-1.0.0-app.bin` | `0x10000` | **Application Only**: Upgrade image that **preserves existing pet NVS state** | ~1.4 MB |
| `bipkins-cyd-1.0.0-bootloader.bin` | `0x1000` | ESP32 2nd stage bootloader | ~25 KB |
| `bipkins-cyd-1.0.0-partitions.bin` | `0x8000` | Custom 2 MB partition table | ~3 KB |
| `bipkins-cyd-1.0.0-boot_app0.bin` | `0xe000` | ESP32 OTA / boot data structure | ~8 KB |
| `manifest.json` | - | Build metadata, toolchain versions, and component hashes | - |
| `SHA256SUMS` | - | Cryptographic SHA-256 checksums of all release binaries | - |

### Checksums

```text
49d4847bacf51592a1cd12cc1ee069db5ac5b8726e63741be3ffb0c9d6e679cb  bipkins-cyd-1.0.0-app.bin
f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0  bipkins-cyd-1.0.0-boot_app0.bin
ed87b6c2a1a808d202ae35d82fc30f32233bb5afdaeb19cbb685a7612c4e2171  bipkins-cyd-1.0.0-bootloader.bin
dcc460bcf4db87aad6ddc64b8448493def25aeb05de195df9d1de86dfdb08800  bipkins-cyd-1.0.0-full.bin
b04ba681eca2feb3b65cb564a6e7961c3caf9beecf21445b0fc2ad087c53a550  bipkins-cyd-1.0.0-partitions.bin
```

---

## 🚀 Installation & Flashing Instructions

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
  0x0 bipkins-cyd-1.0.0-full.bin
```

Alternatively, flashing individual components:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x1000  bipkins-cyd-1.0.0-bootloader.bin \
  0x8000  bipkins-cyd-1.0.0-partitions.bin \
  0xe000  bipkins-cyd-1.0.0-boot_app0.bin \
  0x10000 bipkins-cyd-1.0.0-app.bin
```

---

### Option B: Upgrading an Existing Pet (Preserves NVS / Pet State)

> 💡 **Important:** To preserve your pet's name, coins, traits, and birthday in NVS memory, flash **only** the application binary to offset `0x10000`. Do **NOT** use `erase_flash` or flash `0x0`.

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 2MB \
  0x10000 bipkins-cyd-1.0.0-app.bin
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
