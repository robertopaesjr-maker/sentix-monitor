import requests
import re
import os
import hashlib
import smtplib
from email.mime.text import MIMEText

PAGE_URL = "https://www.crypto-sentiment.com/bitcoin-strategic-bias"
LAST_HASH_FILE = "last_hash.txt"
BASE_URL = "https://www.crypto-sentiment.com"

def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def send_email(subject, body):
    host = os.getenv("EMAIL_HOST")
    port = int(os.getenv("EMAIL_PORT", "587"))
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    to = os.getenv("EMAIL_TO")

    if not (host and user and password and to):
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to

    server = smtplib.SMTP(host, port)
    server.starttls()
    server.login(user, password)
    server.sendmail(user, [to], msg.as_string())
    server.quit()

def extract_image_url(html: str) -> str:
    # 1) pega o src completo
    m = re.search(r'<img[^>]+src="([^"]*sntb_bitcoins[^"]*\.png[^"]*)"', html)
    if not m:
        raise Exception("Não encontrei a imagem do gráfico no HTML.")
    src = m.group(1)

    # 2) transforma src relativo em URL absoluta
    if src.startswith("http://") or src.startswith("https://"):
        return src
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return BASE_URL + src
    return BASE_URL + "/" + src

def main():
    # baixa HTML da página
    resp = requests.get(PAGE_URL, timeout=60)
    resp.raise_for_status()
    html = resp.text

    # extrai URL da imagem do gráfico
    image_url = extract_image_url(html)

    # baixa imagem
    img = requests.get(image_url, timeout=60).content

    # gera novo hash
    new_hash = sha256_bytes(img)

    # lê hash anterior
    old_hash = ""
    if os.path.exists(LAST_HASH_FILE):
        with open(LAST_HASH_FILE, "r") as f:
            old_hash = f.read().strip()

    # compara
    if old_hash and new_hash != old_hash:
        msg = f"O gráfico Sentix Bitcoin foi atualizado.\nURL da nova imagem:\n{image_url}"
        send_email("Sentix atualizado (gráfico)", msg)

    # salva hash atual
    with open(LAST_HASH_FILE, "w") as f:
        f.write(new_hash)

if __name__ == "__main__":
    main()
