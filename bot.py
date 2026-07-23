"""
Main Telegram Bot for Visa Status Checking
Supports: Russia, Turkey, Saudi Arabia
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ConversationHandler, ContextTypes, filters
)
from scrapers import VisaChecker
from database import VisaDatabase

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = int(os.getenv('TELEGRAM_USER_ID'))

# Database
db = VisaDatabase('visa_data.db')

# Conversation states
(MENU, 
 REGISTER_NAME, 
 REGISTER_PASSPORT, 
 REGISTER_COUNTRY,
 CHECK_COUNTRY,
 CHECK_PASSPORT,
 VIEW_VISAS) = range(7)

# Keyboards
MAIN_MENU_KEYBOARD = [
    ['📝 Ro\'yxatdan o\'tish', '✅ Visani Tekshirish'],
    ['📋 Mening Vizalarim', '❌ Chiqish']
]

COUNTRIES_KEYBOARD = [
    ['🇷🇺 Rossiya', '🇹🇷 Turkiya'],
    ['🇸🇦 Saudiya Arabistoni', '⬅️ Ortga']
]

# Helper functions
def get_country_code(country_name: str) -> str:
    """Convert country name to code"""
    mapping = {
        '🇷🇺 Rossiya': 'russia',
        '🇹🇷 Turkiya': 'turkey',
        '🇸🇦 Saudiya Arabistoni': 'saudi_arabia'
    }
    return mapping.get(country_name, '')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command handler"""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    
    await update.message.reply_text(
        f"Assalamu alaikum, {user.first_name}! 👋\n\n"
        f"🤖 *Viza Tekshirish Boti*\n\n"
        f"Ushbu bot orqali siz quyidagi davlatlarning viza holatini tekshira olasiz:\n"
        f"• 🇷🇺 Rossiya\n"
        f"• 🇹🇷 Turkiya\n"
        f"• 🇸🇦 Saudiya Arabistoni\n\n"
        f"Pastdagi tugmachalardan birini tanlang:",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True),
        parse_mode='Markdown'
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Main menu handler"""
    user_input = update.message.text
    
    if '📝 Ro\'yxatdan o\'tish' in user_input:
        await update.message.reply_text(
            "📝 *Ro'yxatdan O'tish*\n\n"
            "Iltimos, to'liq ismingizni kiriting (Pasport bo'yicha):",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return REGISTER_NAME
    
    elif '✅ Visani Tekshirish' in user_input:
        await update.message.reply_text(
            "✅ *Visani Tekshirish*\n\n"
            "Qaysi davlatning vizasini tekshirmoqchisiz?",
            reply_markup=ReplyKeyboardMarkup(COUNTRIES_KEYBOARD, one_time_keyboard=True),
            parse_mode='Markdown'
        )
        return CHECK_COUNTRY
    
    elif '📋 Mening Vizalarim' in user_input:
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Siz ro'yxatdan o'tmagansiz. Avval ro'yxatdan o'ting.",
                reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True)
            )
            return MENU
        
        visas = db.get_user_visas(user['id'])
        if not visas:
            await update.message.reply_text(
                "📋 Sizda hozircha viza ma'lumotlari yo'q.",
                reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True)
            )
            return MENU
        
        visa_list = "📋 *Sizning Vizalaringiz:*\n\n"
        for visa in visas:
            visa_list += (
                f"🌍 {visa['country']}\n"
                f"📝 Turi: {visa['visa_type']}\n"
                f"📅 Tugash: {visa['expiry_date']}\n"
                f"⏰ Qolgan: {visa['days_remaining']} kun\n"
                f"✅ Holat: {visa['status']}\n"
                f"{'─' * 30}\n"
            )
        
        await update.message.reply_text(
            visa_list,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True)
        )
        return MENU
    
    elif '❌ Chiqish' in user_input:
        await update.message.reply_text(
            "Xayr! 👋",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    return MENU

async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Register - get name"""
    full_name = update.message.text.strip()
    
    if len(full_name) < 3:
        await update.message.reply_text("❌ Ism juda qisqa. Qayta kiriting:")
        return REGISTER_NAME
    
    context.user_data['full_name'] = full_name
    
    await update.message.reply_text(
        "✅ Raxmat!\n\n"
        "Hozir pasport raqamingizni kiriting:"
    )
    return REGISTER_PASSPORT

async def register_passport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Register - get passport"""
    passport = update.message.text.strip()
    
    if len(passport) < 5:
        await update.message.reply_text("❌ Pasport raqami juda qisqa. Qayta kiriting:")
        return REGISTER_PASSPORT
    
    context.user_data['passport'] = passport
    
    await update.message.reply_text(
        "✅ Ro'yxatdan o'tish yakunlandi!\n\n"
        "Hozir qaysi davlatning vizasini tekshirmoqchisiz?",
        reply_markup=ReplyKeyboardMarkup(COUNTRIES_KEYBOARD, one_time_keyboard=True),
        parse_mode='Markdown'
    )
    return REGISTER_COUNTRY

async def register_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Register - select country and check visa"""
    user_input = update.message.text
    country_code = get_country_code(user_input)
    
    if not country_code:
        await update.message.reply_text("❌ Davlat tanlash kerak. Qayta tanlang:")
        return REGISTER_COUNTRY
    
    if '⬅️' in user_input:
        await update.message.reply_text(
            "Pastdagi tugmachalardan birini tanlang:",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True)
        )
        return MENU
    
    # Save user
    user_id = update.effective_user.id
    full_name = context.user_data.get('full_name')
    passport = context.user_data.get('passport')
    
    db_user_id = db.add_user(user_id, full_name, passport)
    
    # Check visa
    await update.message.reply_text("⏳ Viza ma'lumotlari tekshirilmoqda...", reply_markup=ReplyKeyboardRemove())
    
    try:
        visa_info = VisaChecker.check_visa(country_code, passport, full_name)
        message = VisaChecker.format_visa_info(visa_info, language='uz')
        
        # Save to database
        if 'error' not in visa_info:
            db.add_visa(
                db_user_id,
                visa_info.get('country', 'N/A'),
                visa_info.get('visa_type', 'N/A'),
                visa_info.get('issue_date', ''),
                visa_info.get('expiry_date', '')
            )
        
        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error checking visa: {e}")
        await update.message.reply_text(
            f"❌ Xato yuz berdi: {str(e)}",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True)
        )
    
    return MENU

async def check_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Check visa - select country"""
    user_input = update.message.text
    
    if '⬅️' in user_input:
        await update.message.reply_text(
            "Pastdagi tugmachalardan birini tanlang:",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True)
        )
        return MENU
    
    country_code = get_country_code(user_input)
    
    if not country_code:
        await update.message.reply_text("❌ Davlat tanlash kerak. Qayta tanlang:")
        return CHECK_COUNTRY
    
    context.user_data['check_country'] = country_code
    
    await update.message.reply_text(
        "Iltimos, pasport raqamingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    return CHECK_PASSPORT

async def check_passport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Check visa - get passport and check"""
    passport = update.message.text.strip()
    country_code = context.user_data.get('check_country')
    full_name = "Unknown"
    
    # Get user's full name if registered
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if user:
        full_name = user['full_name']
    
    await update.message.reply_text("⏳ Viza ma'lumotlari tekshirilmoqda...", reply_markup=ReplyKeyboardRemove())
    
    try:
        visa_info = VisaChecker.check_visa(country_code, passport, full_name)
        message = VisaChecker.format_visa_info(visa_info, language='uz')
        
        # Save to database if user exists
        if user and 'error' not in visa_info:
            db.add_visa(
                user['id'],
                visa_info.get('country', 'N/A'),
                visa_info.get('visa_type', 'N/A'),
                visa_info.get('issue_date', ''),
                visa_info.get('expiry_date', '')
            )
        
        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error checking visa: {e}")
        await update.message.reply_text(
            f"❌ Xato yuz berdi: {str(e)}",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, one_time_keyboard=True)
        )
    
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation"""
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Error handler"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Main function to run the bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            REGISTER_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_passport)],
            REGISTER_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_country)],
            CHECK_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_country)],
            CHECK_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_passport)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
