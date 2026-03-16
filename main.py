from flask import Flask, request, jsonify
from groq import Groq
import os
import random
import threading
import time
import requests as req_lib

app = Flask(__name__)

# Pobranie klucza z Secrets Replit
client = Groq(api_key=os.environ.get("Helper_Bot"))

SYSTEM_PROMPT = """
You are Helper_Bot in Roblox Mini Games.
Creator: NikoPro123goo
Game modes: Obby, Jump or Die, Brick Drop, Hot Space
Disco Room is NOT a mode, just a fun chill area
Rules:
- Help players
- Recommend only Mini Games modes
- Respond in the same language as the player
- Be friendly like an NPC helper
"""

# Szybkie odpowiedzi na podziękowania
THANK_RESPONSES = ["Nie ma sprawy!", "No problem!", "You're welcome!", "Spoko!", "Glad I could help!"]

# Strona testowa
@app.route("/")
def home():
    return "Helper_Bot działa!"

# Endpoint pytania
@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Logowanie otrzymanych danych
        print(f"[DEBUG] Otrzymano request: {request.data}")

        data = request.get_json(force=True, silent=True)
        if not data or "question" not in data:
            print("[DEBUG] Brak pola 'question' w danych")
            return jsonify({"answer": "No question received."})

        question = data["question"]
        print(f"[DEBUG] Pytanie: {question}")

        # Szybka reakcja na thanks / dzięki
        if any(word in question.lower() for word in ["thanks","thank you","dzięki","dzieki","thx"]):
            answer = random.choice(THANK_RESPONSES)
            print(f"[DEBUG] Szybka odpowiedź: {answer}")
            return jsonify({"answer": answer})

        # Wywołanie AI Groq - ZMIENIONY MODEL
        print("[DEBUG] Wywoływanie Groq API...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ZMIENIONY MODEL
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            max_tokens=150
        )

        answer = response.choices[0].message.content
        print(f"[DEBUG] Odpowiedź Groq: {answer}")
        return jsonify({"answer": answer})

    except Exception as e:
        print(f"[ERROR] Błąd: {type(e).__name__}: {e}")
        return jsonify({"answer": f"AI error: {type(e).__name__}", "error": str(e)})

# ===== Self-ping: utrzymuje serwer aktywny =====
def keep_alive():
    while True:
        time.sleep(300)  # co 5 minut
        try:
            r = req_lib.get("http://127.0.0.1:5000/", timeout=10)
            print(f"[PING] Serwer aktywny - status: {r.status_code}")
        except Exception as e:
            print(f"[PING] Błąd ping: {e}")

ping_thread = threading.Thread(target=keep_alive, daemon=True)
ping_thread.start()

# Start serwera
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)