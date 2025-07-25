import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI

# 日志
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# 读取环境变量（Railway 上在 Variables 里配置）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # 你也可以写死

if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY 未配置，会导致 /chat、/lc/webhook 无法正常调用。")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def index():
    return "OK. /lc/webhook for LiveChat, /chat for quick test."

@app.route("/chat", methods=["POST"])
def chat():
    """
    本地快速自测用：
    curl -X POST https://<你的-railway-域名>/chat -H "Content-Type: application/json" -d '{"message":"你好"}'
    """
    try:
        data = request.get_json(force=True)
        msg = data.get("message", "")
        if not msg:
            return jsonify({"error": "message is required"}), 400

        reply = call_gpt(msg)
        return jsonify({"response": reply})
    except Exception as e:
        logging.exception("chat error")
        return jsonify({"error": str(e)}), 500

@app.route("/lc/webhook", methods=["POST"])
def lc_webhook():
    """
    LiveChat Chat Webhook 的入口（免 OAuth 方案）：
    在 LiveChat 的 Chat Webhooks 里把 URL 配置成：
    POST https://<你的-railway-域名>/lc/webhook
    触发器选择 incoming_event（或你需要的），
    Body 可直接发整个事件，或者发 event.message.content。
    我这边统一做兼容解析。
    """
    try:
        payload = request.get_json(force=True)
        logging.info(f"LC webhook payload: {payload}")

        # 兼容几种常见结构
        user_text = (
            payload.get("message") or
            (payload.get("event", {}).get("message", {}).get("text")) or
            (payload.get("event", {}).get("message", {}).get("content")) or
            ""
        )

        if not user_text:
            # 没拿到内容，也要返回 200，避免 LC 重试
            return jsonify({"text": "我没有收到可回复的消息"}), 200

        answer = call_gpt(user_text)

        # LiveChat Chat Webhooks 期望的返回字段名一般是 text（你在配置中 Response path= text）
        return jsonify({"text": answer}), 200

    except Exception as e:
        logging.exception("lc_webhook error")
        # 也返回 200，避免 LiveChat 不停重试
        return jsonify({"text": f"服务端异常：{e}"}), 200

def call_gpt(prompt: str) -> str:
    """
    调 OpenAI 的最小封装。
    """
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY 未配置，无法回答。"

    # 新版 openai SDK（openai>=1.x）
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()

if __name__ == "__main__":
    # 本地调试时用，Railway 会用 gunicorn + $PORT
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
