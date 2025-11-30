import requests
import re
import os
import hashlib
import smtplib
from email.mime.text import MIMEText

PAGE_URL = "https://www.crypto-sentiment.com/bitcoin-strategic-bias"
LAST_HASH_FILE = "last_hash.txt"

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
    match = re.search(r'sntb_bitcoins-[a-zA-Z0-9]+\\.png', html)
    if not match:
        raise Exception("Imagem do gráfico não encontrada na página.")
    filename = match.group(0)
    return "https://www.crypto-sentiment.com/templates/yootheme/cache/d7/" + filename

def main():
    # Baixa o HTML da página
    html = requests.get(PAGE_URL, timeout=60).text

    # Extrai o URL exato da imagem
    image_url = extract_image_url(html)

    # Baixa a imagem real
    img_bytes = requests.get(image_url, timeout=60).content

    # Calcula hash
    new_hash = sha256_bytes(img_bytes)

    # Carrega hash anterior
    old_hash = ""
    if os.path.exists(LAST_HASH_FILE):
        with open(LAST_HASH_FILE, "r") as f:
            old_hash = f.read().strip()

    # Compara
    if old_hash and new_hash != old_hash:
        msg = f"O gráfico Sentix Bitcoin foi atualizado.\nNova imagem: {image_url}"
        send_email("Sentix atualizado (gráfico)", msg)

    # Salva hash
    with open(LAST_HASH_FILE, "w") as f:
        f.write(new_hash)

if __name__ == "__main__":
    main()
