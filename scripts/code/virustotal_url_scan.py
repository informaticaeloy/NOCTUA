import sys
import json
import requests

def scan_url(api_key, url):
    headers = {
        "x-apikey": api_key
    }
    data = {
        "url": url
    }

    # Paso 1: enviar la URL para escaneo
    submit_resp = requests.post(
        "https://www.virustotal.com/api/v3/urls",
        headers=headers,
        data=data
    )
    if submit_resp.status_code != 200:
        print(f"[!] Error al enviar URL: {submit_resp.text}", file=sys.stderr)
        sys.exit(1)

    url_id = submit_resp.json()["data"]["id"]

    # Paso 2: consultar resultados
    result_resp = requests.get(
        f"https://www.virustotal.com/api/v3/analyses/{url_id}",
        headers=headers
    )

    if result_resp.status_code != 200:
        print(f"[!] Error al obtener resultados: {result_resp.text}", file=sys.stderr)
        sys.exit(1)

    return result_resp.json()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: virustotal_url_scan.py <url> <VT_API_KEY>")
        sys.exit(1)

    target_url = sys.argv[1]
    vt_key = sys.argv[2]
    result = scan_url(vt_key, target_url)

    print(json.dumps(result, indent=2))
