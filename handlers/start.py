# This file handles start and basic command handlers
# it defines start_command and cancel_command functions

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from utils.logger import logger

# Context: this function is used within the application to handle /start command
# and welcome users to the bot
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    welcome_message = (
        f"👋 Привіт, {user_name}!\n\n"
        f"🤖 Це бот для обліку прибутків.\n\n"
        f"💡 Бот автоматично надсилає запити:\n"
        f"• 📅 Щоденно о 18:50 - запит планового прибутку\n"
        f"• 📅 Останній день місяця о 19:00 - запит фактичного прибутку\n"
        f"• 📊 1-го числа о 09:00 - звіт адміну\n\n"
        f"❓ Просто відповідайте на запити боту!\n\n"
        f"📋 Для перегляду всіх команд використайте /help"
    )
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')
    logger.info("Користувач %s викликав /start", user_id)

# Context: this handler is used within the application to show help message
# with all available commands and their descriptions
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message with all available commands"""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    help_message = (
        f"📋 *Доступні команди:*\n\n"
        f"🏠 *Основні:*\n"
        f"• /start - Привітання та опис бота\n"
        f"• /help - Показати цю довідку\n"
        f"• /cancel - Скасувати поточну дію\n\n"
        f"💰 *Облік прибутків:*\n"
        f"• /ask\\_potential - Запросити ввод планового прибутку\n"
        f"• /ask\\_fact - Запросити ввод фактичного прибутку\n\n"
        f"📊 *Звіти:*\n"
        f"• /monthly\\_report - Показати місячний звіт\n\n"
        f"🤖 *Автоматичні функції:*\n"
        f"• Щоденно о 18:50 - запит планового прибутку\n"
        f"• Останній день місяця о 19:00 - запит фактичного прибутку\n"
        f"• 1-го числа о 09:00 - звіт адміну\n\n"
        f"❓ *Як користуватися:*\n"
        f"Просто відповідайте на запити боту або використовуйте команди вище\\."
    )
    
    await update.message.reply_text(help_message, parse_mode='Markdown')
    logger.info("Користувач %s викликав /help", user_id)

# Context: this handler is used within the application to cancel current ForceReply state
# and provide user-friendly feedback about cancellation
async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation and clear ForceReply state"""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    
    # Check if user has any active state that can be cancelled
    user_data = context.user_data
    if user_data is None:
        user_data = {}
        
    has_active_state = bool(user_data.get('force_reply_active') or 
                           user_data.get('waiting_for_fact') or
                           user_data.get('waiting_for_potential'))
    
    if has_active_state:
        # Clear all possible states
        user_data.clear()
        
        # Send confirmation with context about what was cancelled
        await update.message.reply_text(
            "✅ Операцію скасовано.\n"
            "Ви можете почати заново або використати /start для перегляду команд.",
            reply_markup=ReplyKeyboardRemove()
        )
        logger.info("User %s cancelled active operation", user_id)
    else:
        # No active state to cancel
        await update.message.reply_text(
            "ℹ️ Немає активних операцій для скасування.\n"
            "Використайте /start для перегляду доступних команд."
        )
        logger.info("User %s tried to cancel but no active operation", user_id)
    
    return ConversationHandler.END