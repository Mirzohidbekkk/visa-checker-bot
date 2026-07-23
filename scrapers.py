"""
Visa scrapers for different countries
Supports: Russia, Turkey, Saudi Arabia
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VisaChecker:
    """Main visa checker class"""
    
    BASE_URLS = {
        'russia': 'https://www.mfa.gov.ru/en/visa/',
        'turkey': 'https://www.evisa.gov.tr/en/',
        'saudi_arabia': 'https://www.visitsaudi.com/en/'
    }
    
    @staticmethod
    def check_visa(country: str, passport: str, full_name: str) -> dict:
        """
        Check visa status for a specific country
        
        Args:
            country: Country code (russia, turkey, saudi_arabia)
            passport: Passport number
            full_name: Full name of the person
            
        Returns:
            Dictionary with visa information
        """
        try:
            if country == 'russia':
                return VisaChecker._check_russia_visa(passport, full_name)
            elif country == 'turkey':
                return VisaChecker._check_turkey_visa(passport, full_name)
            elif country == 'saudi_arabia':
                return VisaChecker._check_saudi_visa(passport, full_name)
            else:
                return {'error': 'Unknown country'}
        except Exception as e:
            logger.error(f"Error checking visa for {country}: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def _check_russia_visa(passport: str, full_name: str) -> dict:
        """
        Check Russia visa status
        Simulates FMS API check
        """
        try:
            # Simulate API call
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # In production, this would call actual FMS API
            # For now, we simulate a response
            visa_info = {
                'country': 'Russia',
                'visa_type': 'Tourist Visa',
                'issue_date': '01.01.2024',
                'expiry_date': '31.12.2024',
                'status': 'active',
                'days_remaining': VisaChecker._calculate_days_remaining('31.12.2024')
            }
            
            logger.info(f"Russia visa checked for {passport}")
            return visa_info
            
        except Exception as e:
            logger.error(f"Error checking Russia visa: {str(e)}")
            return {'error': f'Failed to check Russia visa: {str(e)}'}
    
    @staticmethod
    def _check_turkey_visa(passport: str, full_name: str) -> dict:
        """
        Check Turkey e-Visa status
        Simulates e-Visa API check
        """
        try:
            # In production, this would call actual e-Visa API
            visa_info = {
                'country': 'Turkey',
                'visa_type': 'e-Visa',
                'issue_date': '15.03.2024',
                'expiry_date': '15.09.2024',
                'status': 'active',
                'days_remaining': VisaChecker._calculate_days_remaining('15.09.2024')
            }
            
            logger.info(f"Turkey visa checked for {passport}")
            return visa_info
            
        except Exception as e:
            logger.error(f"Error checking Turkey visa: {str(e)}")
            return {'error': f'Failed to check Turkey visa: {str(e)}'}
    
    @staticmethod
    def _check_saudi_visa(passport: str, full_name: str) -> dict:
        """
        Check Saudi Arabia tourist e-Visa status
        """
        try:
            # In production, this would call actual Saudi e-Visa API
            visa_info = {
                'country': 'Saudi Arabia',
                'visa_type': 'Tourist e-Visa',
                'issue_date': '20.05.2024',
                'expiry_date': '20.08.2024',
                'status': 'active',
                'days_remaining': VisaChecker._calculate_days_remaining('20.08.2024')
            }
            
            logger.info(f"Saudi Arabia visa checked for {passport}")
            return visa_info
            
        except Exception as e:
            logger.error(f"Error checking Saudi Arabia visa: {str(e)}")
            return {'error': f'Failed to check Saudi Arabia visa: {str(e)}'}
    
    @staticmethod
    def _calculate_days_remaining(expiry_date: str) -> int:
        """
        Calculate days remaining until visa expiry
        
        Args:
            expiry_date: Date in format DD.MM.YYYY
            
        Returns:
            Number of days remaining
        """
        try:
            exp_date = datetime.strptime(expiry_date, '%d.%m.%Y')
            today = datetime.now()
            remaining = (exp_date - today).days
            return max(0, remaining)
        except:
            return 0
    
    @staticmethod
    def format_visa_info(visa_info: dict, language: str = 'uz') -> str:
        """
        Format visa information for display
        
        Args:
            visa_info: Dictionary with visa information
            language: Language code (uz, en, ru)
            
        Returns:
            Formatted string for display
        """
        if 'error' in visa_info:
            return f"❌ Xato: {visa_info['error']}"
        
        country = visa_info.get('country', 'N/A')
        visa_type = visa_info.get('visa_type', 'N/A')
        issue_date = visa_info.get('issue_date', 'N/A')
        expiry_date = visa_info.get('expiry_date', 'N/A')
        status = visa_info.get('status', 'N/A')
        days_remaining = visa_info.get('days_remaining', 0)
        
        # Determine status emoji
        if days_remaining > 30:
            status_emoji = '🔊'
        elif days_remaining > 7:
            status_emoji = '⚠️'
        else:
            status_emoji = '❌'
        
        if language == 'uz':
            formatted = (
                f"🌍 *{country}* Vizasi\n\n"
                f"📝 Turi: {visa_type}\n"
                f"📅 Boshlanish: {issue_date}\n"
                f"📅 Tugash: {expiry_date}\n"
                f"{status_emoji} Qolgan: {days_remaining} kun\n"
                f"✅ Holat: {status.upper()}\n\n"
            )
        elif language == 'en':
            formatted = (
                f"🌍 *{country}* Visa\n\n"
                f"📝 Type: {visa_type}\n"
                f"📅 Issued: {issue_date}\n"
                f"📅 Expires: {expiry_date}\n"
                f"{status_emoji} Days Left: {days_remaining}\n"
                f"✅ Status: {status.upper()}\n\n"
            )
        else:  # Russian
            formatted = (
                f"🌍 *{country}* Виза\n\n"
                f"📝 Тип: {visa_type}\n"
                f"📅 Выдана: {issue_date}\n"
                f"📅 Истекает: {expiry_date}\n"
                f"{status_emoji} Осталось: {days_remaining} дней\n"
                f"✅ Статус: {status.upper()}\n\n"
            )
        
        return formatted
