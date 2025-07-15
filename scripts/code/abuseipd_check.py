import sys
import json
import requests

def check_abuseipdb(ip, api_key):
    url = "https://api.abuseipdb.com/api/v2/check"
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    headers = {"Accept": "application/json", "Key": api_key}

    response = requests.get(url, headers=headers, params=params)
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: abuseipdb_check.py <IP> <API_KEY>")
        sys.exit(1)

    ip = sys.argv[1]
    api_key = sys.argv[2]
    result = check_abuseipdb(ip, api_key)
    print(json.dumps(result, indent=2))
