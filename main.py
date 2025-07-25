import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 到 Railway Variables 里填
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY 没配！去 Railway → Variables 里加。")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "GPT Webhook is running! POST to /webhook"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True) or {}
    user_message = (
        data.get("message")
        or data.get("text")
        or data.get("content")
        or ""
    )

    if not user_message:
        return jsonify({"reply": "No message provided"}), 400

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Eres un asesor de atención al cliente para un sitio de apuestas en México. Responde breve, claro y en español mexicano."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            max_tokens=300
        )
        answer = resp.choices[0].message.content.strip()
        return jsonify({"reply": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
