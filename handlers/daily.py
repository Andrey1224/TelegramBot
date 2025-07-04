# This file handles daily workflow handlers
# it defines ask_potential, save_potential, dispatch_potential_prompts, send_admin_digest functions

import os
from datetime import date
from telegram import ForceReply
from telegram.ext import ContextTypes
from services.crud import create_report, get_users_by_geo, DuplicateReportError
from services.reports import get_today_summary, format_summary_markdown
from utils.logger import logger

# Context: this function is used within the application to send potential profit prompts
# to managers with ForceReply for easy input
async def ask_potential(update, context):
    """Send potential profit prompt to manager with ForceReply"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    message = (
        f"👋 {user_name}, доброго дня!\n\n"
        f"Будь ласка, введіть плановий прибуток на сьогодні:\n"
        f"💰 **Введіть суму у гривнях**"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=ForceReply(selective=True),
        parse_mode='Markdown'
    )
    logger.info("Відправлено запит на плановий прибуток користувачу=%s", user_id)

# Context: this function is used within the application to save potential profit data
# from ForceReply messages and handle duplicate entries
async def save_potential(update, context):
    """Save potential profit from ForceReply message"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    text = update.message.text.strip()
    
    try:
        # Parse amount from text
        amount = int(text.replace(' ', '').replace(',', ''))
        if amount <= 0:
            await update.message.reply_text("❌ Сума повинна бути додатнім числом!")
            return
            
    except ValueError:
        await update.message.reply_text("❌ Будь ласка, введіть коректну суму (тільки цифри)!")
        return
    
    try:
        # Get user's office and geo info
        users_data = await get_users_by_geo()
        user_office = None
        user_geo = None
        
        for user_row in users_data:
            user, geo, office = user_row
            if user.tg_id == user_id:
                user_office = office
                user_geo = geo
                break
        
        if not user_office or not user_geo:
            await update.message.reply_text("❌ Ваш акаунт не прив'язаний до офісу або регіону!")
            return
        
        # Save report
        await create_report(
            office_id=user_office.id,
            geo_id=user_geo.id,
            report_date=date.today(),
            amount=amount
        )
        
        await update.message.reply_text(
            f"✅ **Збережено!**\n\n"
            f"Офіс: {user_office.name}\n"
            f"Регіон: {user_geo.name}\n"
            f"Сума: {amount:,} ₴",
            parse_mode='Markdown'
        )
        
    except DuplicateReportError:
        await update.message.reply_text("⚠️ Сьогодні вже введено! Дублювання не дозволяється.")
    except Exception as e:
        logger.error("Помилка збереження планового прибутку для користувача=%s: %s", user_id, str(e))
        await update.message.reply_text("❌ Сталася помилка при збереженні. Спробуйте пізніше.")

# Context: this function is used within the application to dispatch daily prompts
# to all active managers for their respective GEOs
async def dispatch_potential_prompts(context: ContextTypes.DEFAULT_TYPE):
    """Dispatch potential profit prompts to all managers"""
    try:
        users_data = await get_users_by_geo()
        
        if not users_data:
            logger.warning("Не знайдено користувачів для щоденного запиту")
            return
        
        sent_count = 0
        for user_row in users_data:
            user, geo, office = user_row
            try:
                message = (
                    f"📅 **Щоденний запит планового прибутку**\n\n"
                    f"Офіс: {office.name}\n"
                    f"Регіон: {geo.name}\n\n"
                    f"Будь ласка, введіть плановий прибуток на сьогодні:"
                )
                
                await context.bot.send_message(
                    chat_id=user.tg_id,
                    text=message,
                    reply_markup=ForceReply(selective=True),
                    parse_mode='Markdown'
                )
                sent_count += 1
                logger.info("Відправлено щоденний запит користувачу=%s офіс=%s регіон=%s", user.tg_id, office.name, geo.name)
                
            except Exception as e:
                logger.error("Не вдалося відправити запит користувачу=%s: %s", user.tg_id, str(e))
        
        logger.info("Щоденні запити відправлено: %d/%d", sent_count, len(users_data))
        
    except Exception as e:
        logger.error("Помилка у dispatch_potential_prompts: %s", str(e))

# Context: this function is used within the application to send daily digest
# to admin with summary of all planned amounts
async def send_admin_digest(context: ContextTypes.DEFAULT_TYPE):
    """Send daily digest to admin"""
    try:
        admin_id = os.getenv("ADMIN_TG_ID")
        if not admin_id:
            logger.error("ADMIN_TG_ID не налаштовано")
            return
        
        admin_id = int(admin_id)
        
        # Get today's summary
        summary_data = await get_today_summary()
        
        # Format as markdown
        digest_text = format_summary_markdown(summary_data)
        
        # Send to admin
        await context.bot.send_message(
            chat_id=admin_id,
            text=digest_text,
            parse_mode='Markdown'
        )
        
        logger.info("Щоденний дайджест відправлено адміну=%s з %d записами", admin_id, len(summary_data))
        
    except Exception as e:
        logger.error("Помилка відправки дайджесту адміну: %s", str(e))