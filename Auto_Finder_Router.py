# network_scanner.py
import scapy.all as scapy
from mac_vendor_lookup import MacLookup

import socket
import subprocess
import ipaddress

from config import Producent


def arp_scan(network):
    arp = scapy.ARP(pdst=str(network))
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = scapy.srp(packet, timeout=3, verbose=0)[0]
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    return devices

def Check_MacLookup(device, mac_lookup):
    mac_address = device['mac']
    ip_address = device['ip']
    try:
        vendor = mac_lookup.lookup(mac_address)
        for item in Producent:
            if item in vendor.lower():
                # Zwracamy urządzenie z dodatkowymi informacjami
                return {
                    'ip': ip_address,
                    'mac': mac_address,
                    'vendor': vendor
                }
    except KeyError:
        pass
    return None

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

def get_ip_network_with_mask():
    ip = get_ip_address()
    proc = subprocess.Popen('ipconfig', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subnet_mask = None
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if ip.encode() in line:
            for _ in range(2):
                line = proc.stdout.readline()
                if b"Maska podsieci" in line or b"Subnet Mask" in line:
                    subnet_mask = line.rstrip().split(b':')[-1].strip().decode()
                    break
            break
    if subnet_mask is None:
        subnet_mask = '255.255.255.0'

    mask_bits = sum([bin(int(x)).count('1') for x in subnet_mask.split('.')])
    cidr = f"{ip}/{mask_bits}"

    network = ipaddress.IPv4Network(cidr, strict=False)
    return network

def Auto_Finder_Router():
    mac_lookup = MacLookup()
    mac_lookup.update_vendors()
    network = get_ip_network_with_mask()
    devices = arp_scan(network)
    found_devices = []
    for device in devices:
        result = Check_MacLookup(device=device, mac_lookup=mac_lookup)
        if result:
            found_devices.append(result)
    return found_devices
