# This file handles the main application entry point
# it defines ApplicationBuilder, JobQueue setup and command handlers

import os
from datetime import time
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from utils.logger import logger

# Context: this function is used within the application to load environment variables
# and validate required settings
def load_env_variables():
    """Load and validate environment variables"""
    load_dotenv()
    
    bot_token = os.getenv("BOT_TOKEN")
    admin_tg_id = os.getenv("ADMIN_TG_ID")
    
    if not bot_token:
        raise ValueError("BOT_TOKEN не знайдено в змінних середовища")
    
    if not admin_tg_id:
        raise ValueError("ADMIN_TG_ID не знайдено в змінних середовища")
    
    return bot_token, admin_tg_id

# Context: this function is used within the application to handle unified ForceReply
# routing between daily potential and monthly fact handlers
async def unified_reply_handler(update, context):
    """Handle ForceReply messages and route to appropriate handler"""
    if not update.message or not update.message.reply_to_message:
        return
    
    reply_text = update.message.reply_to_message.text
    message_text = update.message.text.strip()
    
    # Check if it's a fact request (monthly)
    if "фактичний прибуток" in reply_text or "місячний" in reply_text.lower():
        from handlers.monthly import save_fact
        await save_fact(update, context)
    # Check if it's a potential request (daily)
    elif "плановий прибуток" in reply_text or "щоденний" in reply_text.lower():
        from handlers.daily import save_potential
        await save_potential(update, context)
    else:
        # Default to daily handler for backward compatibility
        from handlers.daily import save_potential
        await save_potential(update, context)

# Context: this function is used within the application to dispatch daily potential prompts
# to all active managers for their GEOs
async def dispatch_potential_prompts(context):
    from handlers.daily import dispatch_potential_prompts as dispatch_prompts
    await dispatch_prompts(context)

# Context: this function is used within the application to send daily digest
# to admin with summary of planned amounts
async def send_admin_digest(context):
    from handlers.daily import send_admin_digest as send_digest
    await send_digest(context)

# Context: this function is used within the application to dispatch monthly fact prompts
# to all active managers for their GEOs
async def ask_fact_all(context):
    from handlers.monthly import ask_fact_all as ask_facts
    from utils.schedule import next_last_day
    
    # Check if there's already a pending job to avoid duplicates
    existing_jobs = [job for job in context.job_queue.jobs() if job.name == 'ask_fact_all']
    if len(existing_jobs) > 1:
        logger.warning("Multiple ask_fact_all jobs detected, skipping reschedule")
        return
    
    try:
        await ask_facts(context)
        logger.info("ask_fact_all completed successfully")
    except Exception as e:
        logger.error("Ошибка в ask_fact_all: %s", str(e))
    finally:
        # Always reschedule, even if failed (with small delay to avoid immediate retry)
        import asyncio
        await asyncio.sleep(1)  # Small delay to ensure current job is cleaned up
        
        # Remove any existing jobs with same name before rescheduling
        for job in context.job_queue.jobs():
            if job.name == 'ask_fact_all' and job != context.job:
                job.schedule_removal()
        
        context.job_queue.run_once(ask_fact_all, when=next_last_day(19, 0), name='ask_fact_all')
        logger.info("Автоперепланирование ask_fact_all на следующий месяц")

# Context: this function is used within the application to send monthly report
# to admin with plan vs fact comparison
async def monthly_report(context):
    from handlers.monthly import monthly_report as send_report
    from utils.schedule import next_first_day
    
    # Check if there's already a pending job to avoid duplicates
    existing_jobs = [job for job in context.job_queue.jobs() if job.name == 'monthly_report']
    if len(existing_jobs) > 1:
        logger.warning("Multiple monthly_report jobs detected, skipping reschedule")
        return
    
    try:
        await send_report(context)
        logger.info("monthly_report completed successfully")
    except Exception as e:
        logger.error("Ошибка в monthly_report: %s", str(e))
    finally:
        # Always reschedule, even if failed (with small delay to avoid immediate retry)
        import asyncio
        await asyncio.sleep(1)  # Small delay to ensure current job is cleaned up
        
        # Remove any existing jobs with same name before rescheduling
        for job in context.job_queue.jobs():
            if job.name == 'monthly_report' and job != context.job:
                job.schedule_removal()
        
        context.job_queue.run_once(monthly_report, when=next_first_day(9, 0), name='monthly_report')
        logger.info("Автоперепланирование monthly_report на следующий месяц")

# Load environment variables
BOT_TOKEN, ADMIN_TG_ID = load_env_variables()

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Add command handlers
# Import handlers
from handlers.start import start_command, help_command, cancel_handler
from handlers.monthly import ask_fact
from handlers.daily import ask_potential

# Context: this function is used within the application to handle /monthly_report command
# and send report to the user who requested it
async def monthly_report_command(update, context):
    """Handle /monthly_report command"""
    from handlers.monthly import monthly_report
    from services.reports import get_monthly_delta, format_monthly_report_markdown
    from utils.schedule import previous_month_string
    
    try:
        # Get previous month's summary
        prev_month_str = previous_month_string()
        delta_data = await get_monthly_delta(prev_month_str)
        
        # Format as markdown
        report_text = format_monthly_report_markdown(delta_data, prev_month_str)
        
        # Send to user who requested it
        await update.message.reply_text(
            report_text,
            parse_mode='Markdown'
        )
        
        logger.info("Місячний звіт відправлено користувачу=%s за місяць=%s", update.effective_user.id, prev_month_str)
        
    except Exception as e:
        logger.error("Помилка відправки місячного звіту користувачу=%s: %s", update.effective_user.id, str(e))
        await update.message.reply_text("❌ Сталася помилка при формуванні звіту. Спробуйте пізніше.")

# Register handlers
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("cancel", cancel_handler))
app.add_handler(CommandHandler("ask_potential", ask_potential))
app.add_handler(CommandHandler("ask_fact", ask_fact))
app.add_handler(CommandHandler("monthly_report", monthly_report_command))

# Add message handler for ForceReply
app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, unified_reply_handler))

# Context: this function is used within the application to handle errors
# and provide user-friendly error messages
async def error_handler(update, context):
    """Log errors and notify user about issues"""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Try to send a user-friendly error message
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Сталася помилка при обробці команди. Спробуйте пізніше або зверніться до адміністратора."
            )
        except Exception as e:
            logger.error("Failed to send error message to user: %s", str(e))

# Add error handler
app.add_error_handler(error_handler)

# Context: this function is used within the application to setup JobQueue
# with proper error handling and validation
# 1. зарегистрировать JobQueue
jq = app.job_queue

if jq is None:
    raise RuntimeError("JobQueue is not available. Make sure you have APScheduler installed.")

# Daily jobs
# • daily prompt 18 : 50
# jq.run_daily(dispatch_potential_prompts, time=time(18, 50))   # PTB API
# • daily digest 19 : 30
# jq.run_daily(send_admin_digest,        time=time(19, 30))

# Monthly jobs using schedule helpers
from utils.schedule import next_last_day, next_first_day

# • monthly fact request 19:00 on last day of month
jq.run_once(ask_fact_all, when=next_last_day(19, 0), name='ask_fact_all')
# • monthly report 09:00 on 1st day of month
jq.run_once(monthly_report, when=next_first_day(9, 0), name='monthly_report')

# TEMPORARY: Quick testing - run tasks in 10 and 60 seconds
from datetime import timedelta
jq.run_once(dispatch_potential_prompts, when=timedelta(seconds=10), name='dispatch_potential_prompts')
jq.run_once(send_admin_digest, when=timedelta(seconds=60), name='send_admin_digest')

if __name__ == "__main__":
    logger.info("Запуск бота...")
    app.run_polling()                   # запускаем Polling-бота
