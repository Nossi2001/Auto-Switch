import socket
import subprocess
import re
import scapy.all as scapy
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

def get_netmask(ip_address):
    output = subprocess.check_output("ipconfig", encoding='utf-8', errors='ignore')
    netmask = None
    found_ip = False
    for line in output.split('\n'):
        line = line.strip()
        if ip_address in line:
            found_ip = True
        elif found_ip:
            # Szukamy linii z maską podsieci (dla języka polskiego i angielskiego)
            netmask_match = re.search(r'(Maska podsieci|Subnet Mask).*?:\s*([0-9\.]+)', line)
            if netmask_match:
                netmask = netmask_match.group(2)
                break
    return netmask

def calculate_network_address(ip_address, netmask):
    ip_parts = [int(part) for part in ip_address.split('.')]
    mask_parts = [int(part) for part in netmask.split('.')]
    network_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
    network_address = '.'.join(str(part) for part in network_parts)
    return network_address

def arp_scan(network):
    # Tworzymy pakiet ARP zapytujący o wszystkie urządzenia w podanej sieci
    arp = scapy.ARP(pdst=network)
    # Tworzymy ramkę Ethernet z adresem broadcast
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    # Łączymy ramkę Ethernet z pakietem ARP
    packet = ether / arp

    # Wysyłamy pakiet i zbieramy odpowiedzi
    result = scapy.srp(packet, timeout=3, verbose=0)[0]

    # Tworzymy listę urządzeń
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})


if __name__ == "__main__":
    ip_address = get_ip_address()
    print(ip_address)
    netmask = get_netmask(ip_address)
    network_address = calculate_network_address(ip_address, netmask)

    network = f"{network_address}/24"