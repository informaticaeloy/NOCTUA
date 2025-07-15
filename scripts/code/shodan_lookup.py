# scripts/shodan_lookup.py
import sys
import shodan
import json
import os

API_KEY = os.getenv('SHODAN_API_KEY')

def shodan_scan(ip):
    api = shodan.Shodan(API_KEY)
    try:
        host = api.host(ip)
        return json.dumps(host, indent=2)
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python shodan_lookup.py <ip>")
        sys.exit(1)

    ip = sys.argv[1]
    print(shodan_scan(ip))
