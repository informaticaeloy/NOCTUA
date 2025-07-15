import sys
import json
import requests

def lookup_domain(api_key, domain):
    headers = {
        "x-apikey": api_key
    }

    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[!] Error al consultar el dominio: {response.status_code} {response.text}", file=sys.stderr)
        sys.exit(1)

    return response.json()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: virustotal_domain_scan.py <dominio> <VT_API_KEY>")
        sys.exit(1)

    domain = sys.argv[1]
    vt_key = sys.argv[2]

    result = lookup_domain(vt_key, domain)
    print(json.dumps(result, indent=2))
