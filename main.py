from flask import Flask, request, jsonify
from groq import Groq
import os
import random
import threading
import time
import requests as req_lib
import json

app = Flask(__name__)

# ===== GROQ API =====
client = Groq(api_key=os.environ.get("Helper_Bot"))

# ===== LOAD KNOWLEDGE BASE =====
with open("knowledge.json", "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)

# ===== SYSTEM PROMPT =====
SYSTEM_PROMPT = f"""
You are Helper_Bot in Roblox Mini Games.

Creator: {KNOWLEDGE["creator"]}

Game modes (use EXACT definitions):

- Obby:
{KNOWLEDGE["modes"][0]["description"]}

- Jump or Die:
{KNOWLEDGE["modes"][1]["description"]}

- Brick Drop:
{KNOWLEDGE["modes"][2]["description"]}

Place (NOT a game mode):

- Disco Room:
{KNOWLEDGE["places"][0]["description"]}

Rules:
- Never change or invent mechanics
- Be short, clear, NPC-style
- Respond in player's language
"""

# ===== QUICK RESPONSES =====
THANK_RESPONSES = [
    "Nie ma sprawy!",
    "No problem!",
    "You're welcome!",
    "Spoko!",
    "Glad I could help!"
]

# ===== HOME =====
@app.route("/")
def home():
    return "Helper_Bot działa!"

# ===== ASK ENDPOINT =====
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(force=True, silent=True)

        if not data or "question" not in data:
            return jsonify({"answer": "No question received."})

        question = data["question"]
        print(f"[QUESTION] {question}")

        # szybkie thanks
        if any(word in question.lower() for word in ["thanks", "thank you", "dzięki", "dzieki", "thx"]):
            return jsonify({"answer": random.choice(THANK_RESPONSES)})

        # AI CALL
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            max_tokens=250
        )

        answer = response.choices[0].message.content

        return jsonify({"answer": answer})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"answer": f"AI error: {type(e).__name__}", "error": str(e)})

# ===== KEEP ALIVE =====
def keep_alive():
    port = os.environ.get("PORT", "5000")

    while True:
        time.sleep(300)
        try:
            r = req_lib.get(f"http://127.0.0.1:{port}/", timeout=10)
            print(f"[PING] OK {r.status_code}")
        except Exception as e:
            print(f"[PING ERROR] {e}")

threading.Thread(target=keep_alive, daemon=True).start()

# ===== START SERVER =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
