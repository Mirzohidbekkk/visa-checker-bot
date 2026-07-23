"""
Configuration file for visa checker bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_USER_ID = int(os.getenv('TELEGRAM_USER_ID', 0))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///visa_data.db')
    DATABASE_PATH = 'visa_data.db'
    
    # Bot settings
    CHECK_INTERVAL_HOURS = int(os.getenv('CHECK_INTERVAL_HOURS', 24))
    REMINDER_DAYS_BEFORE = int(os.getenv('REMINDER_DAYS_BEFORE', 7))
    
    # Supported countries
    SUPPORTED_COUNTRIES = {
        'russia': {
            'name': 'Rossiya',
            'name_en': 'Russia',
            'emoji': '🇷🇺',
            'scraper': 'RussiaFMSScraper'
        },
        'turkey': {
            'name': 'Turkiya',
            'name_en': 'Turkey',
            'emoji': '🇹🇷',
            'scraper': 'TurkeyEScraper'
        },
        'saudi_arabia': {
            'name': 'Saudiya Arabistoni',
            'name_en': 'Saudi Arabia',
            'emoji': '🇸🇦',
            'scraper': 'SaudiArabiaEScraper'
        }
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")
        if cls.TELEGRAM_USER_ID == 0:
            raise ValueError("TELEGRAM_USER_ID not set in .env")
        return True

# Validate on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️ Configuration warning: {e}")
