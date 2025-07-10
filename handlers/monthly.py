# This file handles monthly workflow handlers
# it defines ask_fact, save_fact, ask_fact_all, monthly_report functions

import os
from telegram import ForceReply, Update
from telegram.ext import ContextTypes
from services.crud import create_fact, get_users_by_geo, get_user_geos, DuplicateFactError
from services.reports import get_monthly_delta, format_monthly_report_markdown
from utils.schedule import current_month_date, previous_month_date, current_month_string, previous_month_string
from utils.logger import logger, telegram_retry

# Context: this function is used within the application to send fact profit prompts
# to managers with ForceReply for easy input
async def ask_fact(update, context):
    """Send fact profit prompt to manager with ForceReply"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    # Запрашиваем факт за завершившийся месяц (так как вызывается в конце месяца)
    target_month_str = current_month_string()
    
    # Get user's geos to show in prompt
    user_geos = await get_user_geos(user_id)
    if not user_geos:
        await update.message.reply_text("❌ Ваш акаунт не прив'язаний до офісу або регіону!")
        return
    
    geo_list = ", ".join([geo.name for geo, office in user_geos])
    office_name = user_geos[0][1].name if user_geos else "Невідомий офіс"
    
    message = (
        f"👋 {user_name}, доброго дня!\n\n"
        f"📅 **Місячний звіт за {target_month_str}**\n\n"
        f"Офіс: {office_name}\n"
        f"Регіони: {geo_list}\n\n"
        f"Будь ласка, введіть фактичний прибуток за місяць:\n"
        f"💰 **Введіть суму у гривнях**\n\n"
        f"ℹ️ *Якщо у вас декілька регіонів, введіть загальну суму*"
    )
    
    await update.message.reply_text(
        message,
        reply_markup=ForceReply(selective=True),
        parse_mode='Markdown'
    )
    logger.info("Відправлено запит на фактичний прибуток користувачу=%s за місяць=%s", user_id, target_month_str)

# Context: this function is used within the application to save fact profit data
# from ForceReply messages and handle duplicate entries
async def save_fact(update, context):
    """Save fact profit from ForceReply message"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    text = update.message.text.strip()
    # Сохраняем факт за завершившийся месяц
    target_month_date = current_month_date()
    target_month_str = current_month_string()
    
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
        
        office_name = user_geos[0][1].name
        
        # If user has multiple geos, we need to handle this case
        if len(user_geos) > 1:
            # For now, we'll save the total amount to the first geo
            # TODO: In future, implement geo-specific input
            geo = user_geos[0][0]
            geo_list = ", ".join([g.name for g, o in user_geos])
            
            await create_fact(
                geo_id=geo.id,
                month=target_month_date,
                amount=amount
            )
            
            await update.message.reply_text(
                f"✅ **Збережено фактичний прибуток!**\n\n"
                f"Офіс: {office_name}\n"
                f"Регіони: {geo_list}\n"
                f"Місяць: {target_month_str}\n"
                f"Сума: {amount:,} ₴\n\n"
                f"ℹ️ *Сума збережена для регіону {geo.name}*",
                parse_mode='Markdown'
            )
        else:
            # Single geo case
            geo = user_geos[0][0]
            
            await create_fact(
                geo_id=geo.id,
                month=target_month_date,
                amount=amount
            )
            
            await update.message.reply_text(
                f"✅ **Збережено фактичний прибуток!**\n\n"
                f"Офіс: {office_name}\n"
                f"Регіон: {geo.name}\n"
                f"Місяць: {target_month_str}\n"
                f"Сума: {amount:,} ₴",
                parse_mode='Markdown'
            )
        
    except DuplicateFactError:
        await update.message.reply_text(f"⚠️ Факт за {target_month_str} вже введено! Дублювання не дозволяється.")
    except Exception as e:
        logger.error("Помилка збереження фактичного прибутку для користувача=%s: %s", user_id, str(e))
        await update.message.reply_text("❌ Сталася помилка при збереженні. Спробуйте пізніше.")

# Context: this function is used within the application to dispatch monthly fact prompts
# to all active managers for their respective GEOs
@telegram_retry(max_retries=3, base_delay=2.0)
async def ask_fact_all(context: ContextTypes.DEFAULT_TYPE):
    """Dispatch fact profit prompts to all managers"""
    try:
        users_data = await get_users_by_geo()
        # Запрашиваем факт за завершающийся месяц
        target_month_str = current_month_string()
        
        if not users_data:
            logger.warning("Не знайдено користувачів для місячного запиту")
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
                    f"📅 **Місячний запит фактичного прибутку**\n\n"
                    f"Офіс: {office.name}\n"
                    f"Регіони: {geo_list}\n"
                    f"Місяць: {target_month_str}\n\n"
                    f"Будь ласка, введіть фактичний прибуток за завершений місяць:\n\n"
                    f"ℹ️ *Якщо у вас декілька регіонів, введіть загальну суму*"
                )
                
                await context.bot.send_message(
                    chat_id=user.tg_id,
                    text=message,
                    reply_markup=ForceReply(selective=True),
                    parse_mode='Markdown'
                )
                sent_count += 1
                logger.info("Відправлено місячний запит користувачу=%s офіс=%s регіони=%s", user.tg_id, office.name, geo_list)
                
            except Exception as e:
                logger.error("Не вдалося відправити місячний запит користувачу=%s: %s", user.tg_id, str(e))
        
        logger.info("Місячні запити відправлено: %d/%d", sent_count, len(users_data))
        
    except Exception as e:
        logger.error("Помилка у ask_fact_all: %s", str(e))

# Context: this function is used within the application to send monthly report
# to admin with plan vs fact comparison
@telegram_retry(max_retries=3, base_delay=2.0)
async def monthly_report(context: ContextTypes.DEFAULT_TYPE):
    """Send monthly report to admin"""
    try:
        admin_id = os.getenv("ADMIN_TG_ID")
        if not admin_id:
            logger.error("ADMIN_TG_ID не налаштовано")
            return
        
        admin_id = int(admin_id)
        
        # Get previous month's summary (reports sent on 1st day for previous month)
        prev_month_str = previous_month_string()
        delta_data = await get_monthly_delta(prev_month_str)
        
        # Format as markdown
        report_text = format_monthly_report_markdown(delta_data, prev_month_str)
        
        # Send to admin
        await context.bot.send_message(
            chat_id=admin_id,
            text=report_text,
            parse_mode='Markdown'
        )
        
        logger.info("Місячний звіт відправлено адміну=%s за місяць=%s", admin_id, prev_month_str)
        
    except Exception as e:
        logger.error("Помилка відправки місячного звіту адміну: %s", str(e))