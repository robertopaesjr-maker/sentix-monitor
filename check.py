import requests

PAGE_URL = "https://www.crypto-sentiment.com/bitcoin-strategic-bias"

def main():
    html = requests.get(PAGE_URL, timeout=60).text
    with open("debug_html.txt", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
