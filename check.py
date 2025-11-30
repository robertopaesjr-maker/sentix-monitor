import requests
import re
import os
import hashlib
import smtplib
from email.mime.text import MIMEText

# --- CONFIGURAÇÃO DOS GRÁFICOS MONITORADOS ---
CHARTS = [
    {
        "name": "Bitcoin Strategic Bias",
        "page": "https://www.crypto-sentiment.com/bitcoin-strategic-bias",
        "pattern": r'sntb_bitcoins[^"]*\.png',
        "hash_file": "last_hash_bias.txt"
    },
    {
        "name": "Bitcoin Sentiment",
        "page": "https://www.crypto-sentiment.com/bitcoin-sentiment",
        "pattern": r'sntm_bitcoins[^"]*\.png',
        "hash_file": "last_hash_sentiment.txt"
    }
]

BASE_URL = "https://www.crypto-sentiment.com"

# ------------------------------------------------

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

def make_absolute_url(src):
    if src.startswith("http://") or src.startswith("https://"):
        return src
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return BASE_URL + src
    return BASE_URL + "/" + src

def extract_image_url(html, pattern):
    m = re.search(r'<img[^>]+src="([^"]*' + pattern + r')"', html)
    if not m:
        raise Exception(f"Imagem do gráfico ({pattern}) não encontrada no HTML.")
    return make_absolute_url(m.group(1))

def monitor_chart(chart):
    # Baixa HTML da página
    html = requests.get(chart["page"], timeout=60).text

    # Extrai URL da imagem
    image_url = extract_image_url(html, chart["pattern"])

    # Baixa imagem
    img = requests.get(image_url, timeout=60).content

    new_hash = sha256_bytes(img)

    # Lê hash anterior
    old_hash = ""
    if os.path.exists(chart["hash_file"]):
        with open(chart["hash_file"], "r") as f:
            old_hash = f.read().strip()

    # Se mudou, envia alerta
    if old_hash and new_hash != old_hash:
        msg = (
            f"O gráfico '{chart['name']}' foi atualizado.\n\n"
            f"URL da nova imagem:\n{image_url}"
        )
        send_email(f"Sentix atualizado: {chart['name']}", msg)

    # Salva hash atual
    with open(chart["hash_file"], "w") as f:
        f.write(new_hash)

def main():
    for chart in CHARTS:
        monitor_chart(chart)

if __name__ == "__main__":
    main()
