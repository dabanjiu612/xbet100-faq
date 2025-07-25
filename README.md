# GPT Webhook (LiveChat auto-reply without OAuth)

1. 在 Railway 的 Variables 里添加：
   - OPENAI_API_KEY=你的 OpenAI Key
   - OPENAI_MODEL=gpt-4o-mini （可选）

2. 部署完成后：
   - 健康检查：GET /
   - 测试：POST /webhook  Body: {"message": "hola"}

3. 在 LiveChat Text Platform → Blocks → Chat Webhooks 配置：
   - Endpoint URL: https://你的域名.up.railway.app/webhook
   - Method: POST
   - Body: { "message": "{{event.message}}" }（或 {{event.message.content}}）
   - Response path: reply
