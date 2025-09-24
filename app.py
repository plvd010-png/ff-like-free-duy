from flask import Flask, request, jsonify
from datetime import datetime
import requests

app = Flask(__name__)

# Lưu lượt like/ngày trong RAM
user_likes = {}
API_URL = "https://ffgarena.vercel.app/like"  # API thật

@app.route("/")
def home():
    return jsonify({"message": "Duydz API is running!"})

@app.route("/like", methods=["GET"])
def like():
    uid = request.args.get("uid")
    region = request.args.get("region")
    key = request.args.get("key")

    # 🔑 Chỉ cho phép key riêng của bạn
    if key != "duydz":
        return jsonify({"error": "Invalid key"}), 403

    if not uid or not region:
        return jsonify({"error": "Missing parameters"}), 400

    today = datetime.now().strftime("%Y-%m-%d")

    if uid not in user_likes or user_likes[uid]["date"] != today:
        user_likes[uid] = {"date": today, "likes": 0}

    if user_likes[uid]["likes"] >= 100:
        return jsonify({
            "error": "Daily limit reached",
            "limit": 100,
            "likes_today": user_likes[uid]["likes"],
            "UID": uid,
            "status": 0
        }), 403

    # 🚀 Gọi API thật
    try:
        r = requests.get(API_URL, params={
            "uid": uid,
            "region": region,
            "key": "ScromnyiDev"   # key API thật
        }, timeout=10)

        data = r.json()

        add_likes = int(data.get("LikesafterCommand", 0)) - int(data.get("LikesbeforeCommand", 0))
        if add_likes <= 0:
            return jsonify({"error": "API did not add likes", "response": data}), 500

        remaining = 100 - user_likes[uid]["likes"]
        if add_likes > remaining:
            add_likes = remaining

        user_likes[uid]["likes"] += add_likes

        return jsonify({
            "LikesGivenByAPI": add_likes,
            "LikesbeforeCommand": data.get("LikesbeforeCommand"),
            "LikesafterCommand": data.get("LikesbeforeCommand", 0) + add_likes,
            "PlayerNickname": data.get("PlayerNickname", f"FB:{uid}"),
            "UID": uid,
            "Region": region,
            "likes_today": user_likes[uid]["likes"],
            "limit": 100,
            "status": 1
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)