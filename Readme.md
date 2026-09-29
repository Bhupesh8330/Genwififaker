# GenWiFiFaker

GenWiFiFaker is a Python tool that creates multiple fake Wi-Fi access points by broadcasting beacon frames. It's designed for wireless security testing, research, and educational purposes.

## Features

- Broadcast up to hundreds of fake Wi-Fi networks
- Random or custom SSID names
- Random or fixed channels (1, 6, 11)
- Lightweight and easy to use
- Works on Linux (Kali) with a compatible wireless adapter
- Windows support (requires Npcap and a compatible adapter, but may not work due to driver limitations)

## Requirements

### Hardware
- **A wireless adapter that supports monitor mode and packet injection.**
  - Recommended chipsets: Atheros AR9271 (e.g., Alfa AWUS036NHA, TP-Link TL-WN722N v1), MediaTek MT7612U (e.g., Panda PAU09).
  - **Your laptop's built-in Wi-Fi adapter will NOT work** in most cases, especially on Windows or in a virtual machine. It must be a dedicated USB adapter known for Linux compatibility.

### Software
- Python 3.7+
- Linux (Kali recommended) or Windows
- On Linux: `aircrack-ng` suite for monitor mode
- On Windows: Npcap (with "Support raw 802.11 traffic" enabled) and a compatible adapter. Windows support is experimental and often blocked by drivers.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/GenWiFiFaker.git
   cd GenWiFiFaker