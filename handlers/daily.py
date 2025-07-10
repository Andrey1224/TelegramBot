# This file handles daily workflow handlers
# it defines ask_potential, save_potential, dispatch_potential_prompts, send_admin_digest functions

import os
from datetime import date
from telegram import ForceReply, Update
from telegram.ext import ContextTypes
from services.crud import create_report, get_users_by_geo, get_user_geos, DuplicateReportError
from services.reports import get_today_summary, format_summary_markdown
from utils.logger import logger, telegram_retry

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
    
    # Parse amount with improved validation
    from utils.logger import parse_amount
    amount, error_message = parse_amount(text)
    
    if error_message:
        await update.message.reply_text(f"❌ {error_message}\n\nСпробуйте ще раз з коректною сумою.")
        return
    
    try:
        # Get user's geos
        user_geos = await get_user_geos(user_id)
        if not user_geos:
            await update.message.reply_text("❌ Ваш акаунт не прив'язаний до офісу або регіону!")
            return
        
        # For daily reports, save to the first geo (or implement geo selection)
        geo = user_geos[0][0]
        office = user_geos[0][1]
        
        # Save report
        await create_report(
            office_id=office.id,
            geo_id=geo.id,
            report_date=date.today(),
            amount=amount
        )
        
        if len(user_geos) > 1:
            geo_list = ", ".join([g.name for g, o in user_geos])
            await update.message.reply_text(
                f"✅ **Збережено!**\n\n"
                f"Офіс: {office.name}\n"
                f"Регіони: {geo_list}\n"
                f"Сума: {amount:,} ₴\n\n"
                f"ℹ️ *Сума збережена для регіону {geo.name}*",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"✅ **Збережено!**\n\n"
                f"Офіс: {office.name}\n"
                f"Регіон: {geo.name}\n"
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
@telegram_retry(max_retries=3, base_delay=2.0)
async def dispatch_potential_prompts(context: ContextTypes.DEFAULT_TYPE):
    """Dispatch potential profit prompts to all managers"""
    try:
        users_data = await get_users_by_geo()
        
        if not users_data:
            logger.warning("Не знайдено користувачів для щоденного запиту")
            return
        
        sent_count = 0
        for user, office in users_data:
            try:
                # Get user's geos for the message
                user_geos = await get_user_geos(user.tg_id)
                if not user_geos:
                    logger.warning("Користувач %s не має прив'язаних регіонів", user.tg_id)
                    continue
                
                geo_list = ", ".join([geo.name for geo, office in user_geos])
                
                message = (
                    f"📅 **Щоденний запит планового прибутку**\n\n"
                    f"Офіс: {office.name}\n"
                    f"Регіони: {geo_list}\n\n"
                    f"Будь ласка, введіть плановий прибуток на сьогодні:\n\n"
                    f"ℹ️ *Якщо у вас декілька регіонів, введіть загальну суму*"
                )
                
                await context.bot.send_message(
                    chat_id=user.tg_id,
                    text=message,
                    reply_markup=ForceReply(selective=True),
                    parse_mode='Markdown'
                )
                sent_count += 1
                logger.info("Відправлено щоденний запит користувачу=%s офіс=%s регіони=%s", user.tg_id, office.name, geo_list)
                
            except Exception as e:
                logger.error("Не вдалося відправити запит користувачу=%s: %s", user.tg_id, str(e))
        
        logger.info("Щоденні запити відправлено: %d/%d", sent_count, len(users_data))
        
    except Exception as e:
        logger.error("Помилка у dispatch_potential_prompts: %s", str(e))

# Context: this function is used within the application to send daily digest
# to admin with summary of all planned amounts
@telegram_retry(max_retries=3, base_delay=2.0)
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