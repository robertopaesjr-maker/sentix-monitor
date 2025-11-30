import requests
import re
import os
import hashlib
import smtplib
from email.mime_text import MIMEText

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

def make_absolute_url(src: str) -> str:
    # já é absoluta
    if src.startswith("http://") or src.startswith("https://"):
        return src
    # protocolo relativo: //dominio/...
    if src.startswith("//"):
        return "https:" + src
    # caminho absoluto no site
    if src.startswith("/"):
        return BASE_URL + src
    # caminho relativo
    return BASE_URL + "/" + src

def extract_image_url(html: str) -> str:
    # procura qualquer src="...sntb_bitcoins...png..."
    m = re.search(r'src="([^"]*sntb_bitcoins[^"]*?\\.png[^"]*)"', html)
    if not m:
        raise Exception("Imagem do gráfico (sntb_bitcoins*.png) não encontrada na página.")
    src = m.group(1)
    return make_absolute_url(src)

def main():
    # baixa HTML da página
    resp = requests.get(PAGE_URL, timeout=60)
    resp.raise_for_status()
    html = resp.text

    # extrai URL exata da imagem do gráfico
    image_url = extract_image_url(html)

    # baixa imagem
    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()
    img_bytes = img_resp.content

    # hash da imagem
    new_hash = sha256_bytes(img_bytes)

    # hash anterior
    old_hash = ""
    if os.path.exists(LAST_HASH_FILE):
        with open(LAST_HASH_FILE, "r") as f:
            old_hash = f.read().strip()

    # compara
    if old_hash and new_hash != old_hash:
        msg = f"O gráfico Sentix Bitcoin foi atualizado.\nNova imagem: {image_url}"
        send_email("Sentix atualizado (gráfico)", msg)

    # salva hash atual
    with open(LAST_HASH_FILE, "w") as f:
        f.write(new_hash)

if __name__ == "__main__":
    main()
