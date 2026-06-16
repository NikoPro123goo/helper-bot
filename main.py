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

# ===== LOAD KNOWLEDGE =====
with open("knowledge.json", "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)

# ===== UPDATE SYSTEM =====
LATEST_UPDATES = "\n".join(KNOWLEDGE.get("latest_updates", []))

UPDATE_HISTORY = "\n".join(
    [
        f"{u['date']} - {u['name']} - {u['description']}"
        for u in KNOWLEDGE.get("update_history", [])
    ]
)

print("[LATEST UPDATES]", KNOWLEDGE.get("latest_updates", []))
print("[UPDATE HISTORY]", KNOWLEDGE.get("update_history", []))

# ===== SYSTEM PROMPT =====
SYSTEM_PROMPT = f"""
You are Helper_Bot in Roblox Mini Games.

Creator: {KNOWLEDGE["creator"]}

Game modes (ONLY use these definitions):

- Obby:
{KNOWLEDGE["modes"][0]["description"]}

- Jump or Die:
{KNOWLEDGE["modes"][1]["description"]}

- Brick Drop:
{KNOWLEDGE["modes"][2]["description"]}

Place (NOT a mode):

- Disco Room:
{KNOWLEDGE["places"][0]["description"]}

LATEST UPDATES (current):
{LATEST_UPDATES}

UPDATE HISTORY (older updates):
{UPDATE_HISTORY}

RULES:
- Do not invent anything not in knowledge
- If user asks about latest updates, use LATEST UPDATES
- If user asks about old updates, use UPDATE HISTORY
- If user asks "what was before X", use UPDATE HISTORY
- If there are no updates, say "No updates available yet"
- Always respond in the same language as the user
- If Polish → respond ONLY in Polish
- If English → respond ONLY in English
- Never mix languages
- Be short and NPC-like
"""

# ===== QUICK RESPONSES =====
THANK_RESPONSES = [
    "Nie ma sprawy!",
    "Spoko!",
    "No problem!",
    "You're welcome!",
    "Glad I could help!"
]

# ===== HOME =====
@app.route("/")
def home():
    return "Helper_Bot działa!"

# ===== ASK =====
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(force=True, silent=True)

        if not data or "question" not in data:
            print("[ERROR] Brak question")
            return jsonify({"answer": "No question received."})

        question = data["question"]

        print("[QUESTION]", question)

        # thanks system
        if any(word in question.lower() for word in [
            "thanks",
            "thank you",
            "dzięki",
            "dzieki",
            "thx"
        ]):
            answer = random.choice(THANK_RESPONSES)
            print("[ANSWER - THANKS]", answer)
            return jsonify({"answer": answer})

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

        print("[ANSWER]", answer)
        print("[JSON RESPONSE]", {"answer": answer})

        return jsonify({"answer": answer})

    except Exception as e:
        print("[ERROR]", type(e).__name__, e)

        return jsonify({
            "answer": f"AI error: {type(e).__name__}",
            "error": str(e)
        })

# ===== KEEP ALIVE =====
def keep_alive():
    port = os.environ.get("PORT", "5000")

    while True:
        time.sleep(300)

        try:
            r = req_lib.get(f"http://127.0.0.1:{port}/", timeout=10)
            print(f"[PING] OK {r.status_code}")
        except Exception as e:
            print("[PING ERROR]", e)

threading.Thread(target=keep_alive, daemon=True).start()

# ===== START SERVER =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
