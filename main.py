# точка входа: создаёт ApplicationBuilder, JobQueue
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

load_dotenv()                            # читает BOT_TOKEN из .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

async def start(update, context):
    await update.message.reply_text("👋 Bot is alive!")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()                   # запускаем Polling-бота
