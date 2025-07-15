# scripts/ip_geolocation.py
import sys
import requests
import json

def geolocate(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
        return json.dumps(res.json(), indent=2)
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python ip_geolocation.py <ip>")
        sys.exit(1)

    ip = sys.argv[1]
    print(geolocate(ip))
