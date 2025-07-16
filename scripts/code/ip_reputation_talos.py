# scripts/ip_reputation_talos.py
import sys
import requests
from bs4 import BeautifulSoup

def get_talos_reputation(ip):
    url = f"https://talosintelligence.com/reputation_center/lookup?search={ip}"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        category = soup.find("div", class_="category-title").get_text(strip=True)
        return f"Talos Reputation: {category}\nURL: {url}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python ip_reputation_talos.py <ip>")
        sys.exit(1)

    ip = sys.argv[1]
    print(get_talos_reputation(ip))
