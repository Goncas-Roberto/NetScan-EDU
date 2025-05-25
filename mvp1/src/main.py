"""
MIT License

Copyright (c) 2025 Goncas-Roberto, rareusernames, VascoSousa070, Joao30sa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os, platform, subprocess, re, socket
from ipaddress import IPv4Network

def obterIpLocal() :

    socketTemporario = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketTemporario.connect(("8.8.8.8",80))
    ip_local = socketTemporario.getsockname()[0]
    socketTemporario.close()
    return  ip_local

def pingIp(ip, tempo) :

    socketTemporario = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketTemporario.connect(("8.8.8.8", 80))

    ip_local = socketTemporario.getsockname()[0]

    socketTemporario.close()
    return ip_local

    return

def obterTabelaARP() :
    arp_table = {}
    if platform.system().lower() == 'windows':
        output = subprocess.check_output(['arp', '-a']).decode('utf-8', errors='ignore')
        lines = output.split('\n')

        for line in lines:
            if 'dynamic' in line.lower():
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1]
                    arp_table[ip] = mac

    else:
        output = subprocess.check_output(['arp', '-a']).decode('utf-8', errors='ignore')
        lines = output.split('\n')
        for line in lines:
            if '(' in line and ')' in line:
                ip = line.split('(')[1].split(')')[0]
                mac_search = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', line)
                mac = mac_search.group(0) if mac_search else None
                if mac:
                    arp_table[ip] = mac
    return arp_table

def escanearRedeLocal() :
    dispositivos = []
    ip_local = obterIpLocal()

    if platform.system().lower() == 'windows':

        output = subprocess.check_output(['ipconfig']).decode('utf-8', errors='ignore')
        mask_search = re.search(r'Subnet Mask . . . . . . . . . . . : (\d+\.\d+\.\d+\.\d+)', output)
        mask = mask_search.group(1) if mask_search else '255.255.255.0'

    else:

        output = subprocess.check_output(['ifconfig']).decode('utf-8', errors='ignore')
        mask_search = re.search(r'netmask (\d+\.\d+\.\d+\.\d+)', output)
        mask = mask_search.group(1) if mask_search else '255.255.255.0'

    network = IPv4Network(f"{ip_local}/{mask}", strict=False)

    for ip in network.hosts():
        ip_str = str(ip)
        if ip_str == ip_local:
            continue

        if pingIp(ip_str,1):
            hostname = None
            try:
                hostname = socket.gethostbyaddr(ip_str)[0]
            except socket.herror:
                pass

            dispositivos.append({
                'ip': ip_str,
                'hostname': hostname,
                'status': 'online'
            })

    tabelaARP = obterTabelaARP()
    for dispositivo in dispositivos:
        dispositivo['mac'] = tabelaARP.get(dispositivo['ip'], 'Desconhecido')
    return dispositivos

def main() :
    print(escanearRedeLocal())
    return

if __name__ == "__main__":
    main()
