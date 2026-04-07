from flask import Flask, request
import requests
import os
from datetime import datetime

TOKEN = "8709592013:AAE5KyygvrXnPIczZfHWjEI2d5NakqFvaGA"
CHAT_ID = "8502961385"

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Server is running 🚀"

@app.route('/upload', methods=['POST'])
def upload():
    data = request.data

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join("uploads", filename)

    # Save image
    with open(filepath, "wb") as f:
        f.write(data)

    # 🔥 SEND IMAGE TO TELEGRAM
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    with open(filepath, "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": photo})

    return "Uploaded + Telegram Sent", 200
    
    data = request.data

    if not data:
        return "No data", 400

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")

    with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
        f.write(data)

    return "Uploaded", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
