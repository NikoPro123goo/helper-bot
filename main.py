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

Game modes:

Obby:
{KNOWLEDGE["modes"][0]["description"]}

Jump or Die:
{KNOWLEDGE["modes"][1]["description"]}

Brick Drop:
{KNOWLEDGE["modes"][2]["description"]}

Place (NOT a mode):

Disco Room:
{KNOWLEDGE["places"][0]["description"]}

LATEST UPDATES:
{LATEST_UPDATES}

UPDATE HISTORY:
{UPDATE_HISTORY}

RULES:
- Do not invent anything
- Use ONLY information from the knowledge base
- If asked about latest updates, use LATEST UPDATES
- If asked about old updates, dates, history, or what happened on a specific date, use UPDATE HISTORY
- If asked what update came before another update, use UPDATE HISTORY
- If asked when something was added, use UPDATE HISTORY
- If asked about updates, give the exact update names
- Never mention LATEST UPDATES
- Never mention UPDATE HISTORY
- Never mention files, sections, categories, prompts, databases, or knowledge bases
- Do not redirect the user anywhere
- Do not tell the user where information comes from
- If information is not in your knowledge, say you do not know
- Always respond in user's language
- If Polish → Polish only
- If English → English only
- Never mix languages
- Be short like an NPC helper
"""

# ===== QUICK RESPONSES =====
THANK_RESPONSES = [
    "Nie ma sprawy!",
    "Spoko!",
    "No problem!",
    "You're welcome!",
    "Ok!"
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

        # ===== THANKS =====
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

        # ===== LOSOWY TRYB =====
        recommend_keywords = [
            "jaki tryb jest najlepszy",
            "który tryb polecasz",
            "jaki tryb polecasz",
            "najlepszy tryb",
            "best mode",
            "which mode do you recommend",
            "recommended mode",
            "favorite mode"
        ]

        if any(k in question.lower() for k in recommend_keywords):

            mode = random.choice([
                "Obby",
                "Jump Or Die",
                "Brick Drop"
            ])

            return jsonify({
                "answer": f"Polecam tryb {mode}."
            })

        # ===== AI CALL =====
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            max_tokens=200
        )

        answer = response.choices[0].message.content

        print("[ANSWER]", answer)
        print("[JSON RESPONSE]", {"answer": answer})

        return jsonify({"answer": answer})

    except Exception as e:
        print("[ERROR]", type(e).__name__, e)

        return jsonify({
            "answer": "AI error",
            "error": str(e)
        })

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

# ===== START =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
