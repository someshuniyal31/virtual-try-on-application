import requests
from datetime import datetime
import socket

# Telegram Bot Setup (replace with your actual values)
BOT_TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Failed to send Telegram alert:", e)

def log_login_attempt(username, success):
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = "Unknown"
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILED"
    log = f"[{time}] {username} login {status} from IP: {ip}"
    
    # Save to file
    with open("login_logs.txt", "a") as f:
        f.write(log + "\n")

    if success:
        send_telegram_alert(f"⚠️ ALERT: {log}")

# Example usage (you would call this from your login function)
# log_login_attempt("test_user", True)