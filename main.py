# This file handles the main application entry point
# it defines ApplicationBuilder, JobQueue setup and command handlers

import os
from datetime import time
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Context: this function is used within the application to load environment variables
# and initialize the bot token
load_dotenv()                            # читает BOT_TOKEN из .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

# Context: this function is used within the application to handle /start command
# and provide basic bot status information
async def start(update, context):
    await update.message.reply_text("👋 Bot is alive!")

# Context: this function is used within the application to dispatch daily potential prompts
# to all active managers for their GEOs
async def dispatch_potential_prompts(context):
    from handlers.daily import dispatch_potential_prompts as dispatch
    await dispatch(context)

# Context: this function is used within the application to send daily digest
# to admin with summary of all planned amounts
async def send_admin_digest(context):
    from handlers.daily import send_admin_digest as send_digest
    await send_digest(context)

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Context: this function is used within the application to setup JobQueue
# with proper error handling and validation
# 1. зарегистрировать JobQueue
jq = app.job_queue

if jq is None:
    raise RuntimeError("JobQueue is not available. Make sure you have APScheduler installed.")

# • daily prompt 18 : 50
# jq.run_daily(dispatch_potential_prompts, time=time(18, 50))   # PTB API
# • daily digest 19 : 30
# jq.run_daily(send_admin_digest,        time=time(19, 30))

# TEMPORARY: Quick testing - run tasks in 10 and 60 seconds
from datetime import timedelta
jq.run_once(dispatch_potential_prompts, when=timedelta(seconds=10))
jq.run_once(send_admin_digest, when=timedelta(seconds=60))

app.add_handler(CommandHandler("start", start))

# Register ForceReply handler for daily potential input
from handlers.daily import save_potential
app.add_handler(MessageHandler(filters.REPLY, save_potential))

if __name__ == "__main__":
    app.run_polling()                   # запускаем Polling-бота
