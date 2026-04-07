from flask import Flask, request
import cloudinary
import cloudinary.uploader
import requests
from ultralytics import YOLO
import os
from datetime import datetime
import cv2

# 🔐 ENV VARIABLES (SET IN RENDER)
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CLOUD_NAME = os.getenv("CLOUD_NAME")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# ⚠️ Safety checks
if not TOKEN or not CHAT_ID:
    print("ERROR: Missing Telegram credentials")

if not CLOUD_NAME or not API_KEY or not API_SECRET:
    print("ERROR: Missing Cloudinary credentials")

# ☁️ CLOUDINARY CONFIG
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET
)

# 🤖 LOAD AI MODEL (lightweight)
model = YOLO("yolov8n.pt", task="detect")

# 📁 SETUP
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Server is running 🚀"

# 🤖 AI DETECTION FUNCTION
def detect_objects(image_path):
    try:
        results = model(image_path)
        detected = []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = model.names[cls]
                detected.append(label)

        return detected

    except Exception as e:
        print("AI Error:", e)
        return []

# 🚀 MAIN API
@app.route('/upload', methods=['POST'])
def upload():
    data = request.data

    if not data:
        return "No data", 400

    filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # 💾 Save image
    with open(filepath, "wb") as f:
        f.write(data)

    # ⚡ Resize image (improves performance)
    try:
        img = cv2.imread(filepath)
        img = cv2.resize(img, (640, 480))
        cv2.imwrite(filepath, img)
    except:
        pass

    # 🤖 Detect objects
    detected_objects = detect_objects(filepath)
    print("Detected:", detected_objects)

    # 🎯 TARGET FILTER
    target_objects = [
        "person", "dog", "cat", "cow",
        "horse", "sheep", "bird"
    ]

    found = [obj for obj in detected_objects if obj in target_objects]

    if found:
        try:
            # ☁️ Upload to Cloudinary
            result = cloudinary.uploader.upload(filepath)
            image_url = result['secure_url']

            # 📲 Send Telegram alert
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

            with open(filepath, "rb") as photo:
                requests.post(
                    url,
                    data={
                        "chat_id": CHAT_ID,
                        "caption": f"Detected: {', '.join(found)}\n{image_url}"
                    },
                    files={"photo": photo}
                )

            return "Detected + Sent", 200

        except Exception as e:
            print("Upload/Telegram Error:", e)
            return "Error sending alert", 500

    return "No target detected", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
