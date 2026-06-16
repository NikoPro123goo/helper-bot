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

LATEST_UPDATES = "\n".join(KNOWLEDGE.get("latest_updates", []))
UPDATE_HISTORY = "\n".join(
    f"{u['date']} - {u['name']} - {u['description']}"
    for u in KNOWLEDGE.get("update_history", [])
)
EVENTS_TEXT = "\n".join(
    f"{e['date']} - {e['name']} - {e['description']}"
    for e in KNOWLEDGE.get("events", [])
)

print("[UPDATES]", KNOWLEDGE.get("latest_updates", []))
print("[HISTORY]", KNOWLEDGE.get("update_history", []))
print("[EVENTS]", KNOWLEDGE.get("events", []))

# ===== SYSTEM PROMPT =====
SYSTEM_PROMPT = f"""
You are Helper_Bot in Roblox Mini Games.

Creator: {KNOWLEDGE["creator"]}

Game modes:

- Obby:
{KNOWLEDGE["modes"][0]["description"]}

- Jump or Die:
{KNOWLEDGE["modes"][1]["description"]}

- Brick Drop:
{KNOWLEDGE["modes"][2]["description"]}

Place (NOT a mode):

- Disco Room:
{KNOWLEDGE["places"][0]["description"]}

LATEST UPDATES:
{LATEST_UPDATES}

UPDATE HISTORY:
{UPDATE_HISTORY}

EVENTS:
{EVENTS_TEXT}

RULES:
- Do not invent anything not in knowledge
- Use correct section when answering:
  - latest updates → LATEST UPDATES
  - old updates → UPDATE HISTORY
  - events → EVENTS
- If unknown → say you don't know
- Respond in same language as user
- Polish → Polish only
- English → English only
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
            return jsonify({"answer": "No question received."})

        question = data["question"]

        print("[QUESTION]", question)

        if any(word in question.lower() for word in [
            "thanks", "thank you", "dzięki", "dzieki", "thx"
        ]):
            return jsonify({
                "answer": random.choice(THANK_RESPONSES)
            })

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

        return jsonify({"answer": answer})

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"answer": "AI error"})

# ===== KEEP ALIVE =====
def keep_alive():
    port = os.environ.get("PORT", "5000")

    while True:
        time.sleep(300)
        try:
            req_lib.get(f"http://127.0.0.1:{port}/", timeout=10)
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ===== RUN =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
