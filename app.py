from flask import Flask, request
import cloudinary
import cloudinary.uploader
import requests
import os
from datetime import datetime

# Telegram
TOKEN = "8709592013:AAE5KyygvrXnPIczZfHWjEI2d5NakqFvaGA"
CHAT_ID = "8502961385"

# Cloudinary config
cloudinary.config(
    cloud_name="dkzqbnipb",
    api_key="991979261691775",
    api_secret="YBquea02-D_sOj47g4A2o7M0mwY"
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Server is running 🚀"

@app.route('/upload', methods=['POST'])
def upload():
    data = request.data

    if not data:
        return "No data", 400

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Save image locally
    with open(filepath, "wb") as f:
        f.write(data)

    # ☁️ Upload to Cloudinary
    result = cloudinary.uploader.upload(filepath)
    image_url = result['secure_url']

    # 📲 Send to Telegram (with link)
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    with open(filepath, "rb") as photo:
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": f"Motion detected!\n{image_url}"
            },
            files={"photo": photo}
        )

    return "Uploaded + Cloudinary + Telegram", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
