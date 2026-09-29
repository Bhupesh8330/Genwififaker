#!/usr/bin/env python3
"""
GenWiFiFaker - Fake Wi-Fi Network Generator
Creates multiple fake Wi-Fi access points by broadcasting beacon frames.
Requires a wireless adapter that supports monitor mode and packet injection.
"""

import sys
import os
import platform
import argparse
import threading
import time
import random
import ctypes

try:
    from faker import Faker
    from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp
    import colorama
    colorama.init(autoreset=True)
except ImportError as e:
    print(f"Missing dependency: {e}. Please install with: pip install -r requirements.txt")
    sys.exit(1)

# --- Admin elevation for Windows (optional, but won't help with injection) ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_windows():
    if platform.system() == "Windows" and not is_admin():
        print("[!] Requesting administrative privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

elevate_windows()

# --- Logo and constants ---
PROJECT_LOGO = f"""{colorama.Fore.LIGHTRED_EX}
   _____        __          ___ ______ _ ______    _             
  / ____|       \ \        / (_)  ____(_)  ____|  | |            
 | |  __  ___ _ _\ \  /\  / / _| |__   _| |__ __ _| | _____ _ __ 
 | | |_ |/ _ \ '_ \ \/  \/ / | |  __| | |  __/ _` | |/ / _ \ '__|
 | |__| |  __/ | | \  /\  /  | | |    | | | | (_| |   <  __/ |   
  \_____|\___|_| |_|\/  \/   |_|_|    |_|_|  \__,_|_|\_\___|_|   
                                                                 
"""

class FakeAccessPoint:
    def __init__(self, interface, count=10, name=None, channel=None, verbose=False):
        self.interface = interface
        self.count = count
        self.custom_ssid = name
        self.channel = channel
        self.verbose = verbose
        self.faker = Faker()
        self.networks = []

    def generate_networks(self):
        """Generate a list of (SSID, MAC) tuples."""
        for _ in range(self.count):
            ssid = (self.custom_ssid or self.faker.domain_word())[:32]
            mac = self.faker.mac_address()
            self.networks.append((ssid, mac))

    def broadcast_beacon(self, ssid, mac):
        """Continuously broadcast a beacon frame for the given SSID and MAC."""
        # Choose a random channel from 1, 6, 11 if not specified
        ch = self.channel if self.channel else random.choice([1, 6, 11])
        
        if self.verbose:
            print(f"{colorama.Fore.CYAN}[*] Broadcasting SSID: {ssid} | MAC: {mac} | Channel: {ch}{colorama.Fore.RESET}")
        else:
            print(f"{colorama.Fore.LIGHTYELLOW_EX}[ {colorama.Fore.LIGHTRED_EX}GenWiFiFaker {colorama.Fore.LIGHTYELLOW_EX}] {colorama.Fore.LIGHTBLUE_EX}»\n"
                  f" SSID: {colorama.Fore.LIGHTYELLOW_EX}{ssid}{colorama.Fore.RESET} - "
                  f"[MAC: {colorama.Fore.LIGHTBLUE_EX}{mac}{colorama.Fore.RESET}] - "
                  f"[CH: {ch}]")

        # Build the packet
        dot11 = Dot11(type=0, subtype=8, addr1="ff:ff:ff:ff:ff:ff", addr2=mac, addr3=mac)
        beacon = Dot11Beacon(cap="ESS")
        ssid_elt = Dot11Elt(ID="SSID", info=ssid, len=len(ssid))
        rates_elt = Dot11Elt(ID="Rates", info=b'\x82\x84\x8b\x96\x0c\x12\x18\x24')
        ds_elt = Dot11Elt(ID="DSset", info=bytes([ch]))
        packet = RadioTap() / dot11 / beacon / ssid_elt / rates_elt / ds_elt

        while True:
            try:
                sendp(packet, inter=0.1, iface=self.interface, verbose=0)
                time.sleep(0.1)  # Send beacon every 100ms
            except Exception as e:
                print(f"{colorama.Fore.RED}[!] Error on {mac} - {ssid}: {e}{colorama.Fore.RESET}")
                break

    def start(self):
        os.system("cls" if platform.system() == "Windows" else "clear")
        print(PROJECT_LOGO)
        
        # Check for root on Linux
        if platform.system() != "Windows" and os.geteuid() != 0:
            print(f"{colorama.Fore.RED}[!] This script must be run as root on Linux.{colorama.Fore.RESET}")
            sys.exit(1)
        
        print(f"{colorama.Fore.LIGHTYELLOW_EX}[ {colorama.Fore.LIGHTRED_EX}GenWiFiFaker {colorama.Fore.LIGHTYELLOW_EX}] {colorama.Fore.LIGHTBLUE_EX}» Interface: {colorama.Fore.GREEN}{self.interface}")
        print(f"{colorama.Fore.LIGHTYELLOW_EX}[ {colorama.Fore.LIGHTRED_EX}GenWiFiFaker {colorama.Fore.LIGHTYELLOW_EX}] {colorama.Fore.LIGHTBLUE_EX}» Number of APs: {colorama.Fore.GREEN}{self.count}")
        print(f"{colorama.Fore.LIGHTYELLOW_EX}[ {colorama.Fore.LIGHTRED_EX}GenWiFiFaker {colorama.Fore.LIGHTYELLOW_EX}] {colorama.Fore.LIGHTBLUE_EX}» SSID Name: {colorama.Fore.GREEN}{self.custom_ssid or 'Random'}")
        
        input(f"\n{colorama.Fore.YELLOW}Press Enter to start broadcasting (CTRL+C to stop)...{colorama.Fore.RESET}")
        
        self.generate_networks()
        
        print(f"{colorama.Fore.LIGHTYELLOW_EX}[ {colorama.Fore.LIGHTRED_EX}GenWiFiFaker {colorama.Fore.LIGHTYELLOW_EX}] {colorama.Fore.LIGHTBLUE_EX}» [*] Starting...")
        
        threads = []
        for ssid, mac in self.networks:
            t = threading.Thread(target=self.broadcast_beacon, args=(ssid, mac), daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.1)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{colorama.Fore.LIGHTYELLOW_EX}[ {colorama.Fore.LIGHTRED_EX}GenWiFiFaker {colorama.Fore.LIGHTYELLOW_EX}] {colorama.Fore.LIGHTBLUE_EX}» {colorama.Fore.RED}Stopped by user. Exiting...")
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="GenWiFiFaker - Broadcast fake Wi-Fi networks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 gen_wifi_faker.py -i wlan0mon -c 20
  sudo python3 gen_wifi_faker.py -i wlan0mon -c 5 -wn MyFakeWiFi
  sudo python3 gen_wifi_faker.py -i wlan0mon -wn FreeWiFi --channel 6
        """
    )
    parser.add_argument("-i", "--interface", required=True, help="Wireless interface in monitor mode (e.g., wlan0mon)")
    parser.add_argument("-c", "--count", type=int, default=10, help="Number of fake networks to create (default: 10)")
    parser.add_argument("-wn", "--name", help="Custom SSID name (optional, random if not provided)")
    parser.add_argument("--channel", type=int, choices=[1,6,11], help="Fixed channel (1, 6, or 11). Random if not specified.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    faker = FakeAccessPoint(
        interface=args.interface,
        count=args.count,
        name=args.name,
        channel=args.channel,
        verbose=args.verbose
    )
    faker.start()

if __name__ == "__main__":
    main()