# 🧠 Dopamine Hijack v1.h (Dopamine Guard Pro)

![System Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Linux-orange)
![Hardware](https://img.shields.io/badge/Hardware-Arduino-00979D)

**Dopamine Guard Pro** is an extreme, hardware-triggered network throttling system designed to break the cycle of doom-scrolling. By combining an Arduino-based physical switch with deep packet inspection and network traffic control (`tc` & `iptables`), this system instantly throttles or blocks dopamine-heavy applications (TikTok, Instagram, YouTube) across multiple devices on a network.

## 🚀 Features

- **Hardware Trigger**: Instantly toggle the lockdown state using a physical button connected to an Arduino.
- **Smart Multi-Device Targeting**: Selectively target specific devices on the network via MAC/IP scanning or apply rules globally.
- **App-Specific Throttling**: Targets specific CDN and API signatures for:
  - 🎵 TikTok
  - 📸 Instagram (Includes deep Meta subnet IP blocking)
  - 🎥 YouTube
- **"Torture Level" Control**: Dynamically adjust network latency (up to 20,000ms) to make doom-scrolling unbearably slow.
- **Relapse Tracking**: Tracks "relapses" (button presses). After 20 relapses, the system goes into a permanent **LOCKDOWN** state.
- **Cyberpunk UI**: Built-in Tkinter fullscreen dashboard for real-time monitoring and control.

## 🛠️ Architecture

### 1. The Physical Layer (`main.cpp`)
A simple, highly responsive Arduino script that reads a physical button connected to `Pin 2` and `GND`. It communicates with the host system over Serial (`9600` baud), continuously sending `BLOCK` or `FREE` states.

### 2. The Network Layer (`blocker.py`)
A Python-based network router script that listens to the Arduino over `/dev/ttyACM0`. When the `BLOCK` signal is received, it executes a series of root-level network commands:
- Uses `tc` (Traffic Control) to artificially inject latency (`netem delay`).
- Uses `iptables` and string matching to mark and throttle packets matching specific application signatures.
- Drops UDP traffic on port 443 for known Meta (Facebook/Instagram) subnets.

## ⚙️ Requirements & Setup

### Prerequisites
- **OS:** Linux (Requires `sudo` privileges for network manipulation).
- **Dependencies:** `python3`, `python-serial`, `tk`, `iproute2` (`tc`, `ip`), `iptables`.
- **Hardware:** Arduino Uno/Nano (or similar), a push-button, and jumper wires.

### Hardware Setup
1. Connect a push-button between **Digital Pin 2** and **GND** on the Arduino.
2. Flash the `main.cpp` code to the Arduino.
3. Connect the Arduino via USB to the Linux host machine.

### Software Configuration
1. Open `blocker.py` and modify the following variables according to your environment:
   - `SERIAL_PORT`: Your Arduino port (e.g., `/dev/ttyACM0`).
   - `IFACE`: Your wireless interface (e.g., `wlp0s20f3`).
   - `KNOWN_DEVICES`: Map MAC addresses to friendly names for the UI.
2. Run the script with root privileges (required for `tc` and `iptables`):
   ```bash
   sudo python3 blocker.py
   ```

## ⚠️ Disclaimer
*This tool manipulates core network routing rules. Ensure you understand the `iptables` and `tc` commands being executed. Use responsibly and only on networks and devices you own or have explicit permission to manage.*
