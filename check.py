import requests
import os
import smtplib
from email.mime.text import MIMEText
from telegram import Bot

URL = "https://www.crypto-sentiment.com/bitcoin-strategic-bias"
LAST_FILE = "last_content.txt"

def send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        Bot(token=token).send_message(chat_id=chat_id, text=message)

def send_email(subject: str, body: str) -> None:
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

def main() -> None:
    resp = requests.get(URL, timeout=60)
    resp.raise_for_status()
    html = resp.text.strip()

    old = ""
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            old = f.read().strip()

    if old and html != old:
        msg = "A página Sentix Strategic Bias foi atualizada:\n" + URL
        send_telegram(msg)
        send_email("Sentix atualizado", msg)

    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
