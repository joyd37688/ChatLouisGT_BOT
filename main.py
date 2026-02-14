import os
import logging
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
from openai import AsyncOpenAI

# =========================
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("Thiếu BOT_TOKEN")

if not OPENAI_API_KEY:
    raise RuntimeError("Thiếu OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# KEEP ALIVE SERVER
# =========================
web_app = Flask(__name__)

@web_app.route("/")
def health():
    return "V-OMEGA ONLINE", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# =========================
# TELEGRAM AI BOT
# =========================
class OmegaBot:

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🚀 V-OMEGA AI ONLINE")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text

        try:
            response = await client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "Bạn là AI thông minh phân tích sâu."},
                    {"role": "user", "content": user_text}
                ]
            )

            ai_reply = response.choices[0].message.content

        except Exception as e:
            ai_reply = f"Lỗi AI: {e}"

        await update.message.reply_text(ai_reply)

    def run(self):

        app = ApplicationBuilder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logging.info("BOT STARTED")

        app.run_polling(drop_pending_updates=True)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    import threading

    threading.Thread(target=run_web, daemon=True).start()

    bot = OmegaBot()
    bot.run()
