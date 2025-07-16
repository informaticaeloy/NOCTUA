import sys
import json
import requests

def lookup_ip(api_key, ip_address):
    headers = {
        "x-apikey": api_key
    }

    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip_address}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[!] Error al consultar la IP: {response.status_code} {response.text}", file=sys.stderr)
        sys.exit(1)

    return response.json()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: virustotal_ip_scan.py <ip> <VT_API_KEY>")
        sys.exit(1)

    ip = sys.argv[1]
    vt_key = sys.argv[2]

    result = lookup_ip(vt_key, ip)
    print(json.dumps(result, indent=2))
