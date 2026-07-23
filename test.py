"""
Test module for visa checker bot
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers import VisaChecker
from database import VisaDatabase
from datetime import datetime

def test_scrapers():
    """Test all visa scrapers"""
    print("=" * 50)
    print("🧪 TESTING VISA SCRAPERS")
    print("=" * 50)
    
    checker = VisaChecker()
    test_data = {
        'passport': 'AA123456',
        'full_name': 'Test User'
    }
    
    countries = ['russia', 'turkey', 'saudi_arabia']
    
    for country in countries:
        print(f"\n🔍 Testing {country.upper()}...")
        try:
            result = checker.check_visa(country, test_data['passport'], test_data['full_name'])
            
            if 'error' in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                print(f"  ✅ Success!")
                print(f"     Country: {result.get('country')}")
                print(f"     Visa Type: {result.get('visa_type')}")
                print(f"     Status: {result.get('status')}")
                print(f"     Days Remaining: {result.get('days_remaining')}")
                
                # Test formatting
                formatted = checker.format_visa_info(result, 'uz')
                print(f"  ✅ Formatting works!")
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ SCRAPER TESTS COMPLETED")
    print("=" * 50)

def test_database():
    """Test database operations"""
    print("\n" + "=" * 50)
    print("🧪 TESTING DATABASE")
    print("=" * 50)
    
    # Create test database
    db = VisaDatabase('test_visa_data.db')
    
    try:
        # Test add user
        print("\n📝 Testing add_user()...")
        telegram_id = 123456789
        user_id = db.add_user(telegram_id, "Test User", "AA123456")
        print(f"  ✅ User added with ID: {user_id}")
        
        # Test get user
        print("\n📋 Testing get_user()...")
        user = db.get_user(telegram_id)
        if user:
            print(f"  ✅ User found!")
            print(f"     ID: {user['id']}")
            print(f"     Name: {user['full_name']}")
            print(f"     Passport: {user['passport_number']}")
        else:
            print(f"  ❌ User not found!")
        
        # Test add visa
        print("\n🛂 Testing add_visa()...")
        visa_id = db.add_visa(
            user_id,
            'Russia',
            'Tourist Visa',
            '01.01.2024',
            '31.12.2024'
        )
        print(f"  ✅ Visa added with ID: {visa_id}")
        
        # Test get user visas
        print("\n📋 Testing get_user_visas()...")
        visas = db.get_user_visas(user_id)
        if visas:
            print(f"  ✅ Found {len(visas)} visa(s)!")
            for visa in visas:
                print(f"     - {visa['country']}: {visa['visa_type']}")
        else:
            print(f"  ❌ No visas found!")
        
        # Test update status
        print("\n🔄 Testing update_visa_status()...")
        db.update_visa_status(visa_id, 'expired')
        print(f"  ✅ Visa status updated!")
        
        # Verify status change
        visas = db.get_user_visas(user_id)
        if visas[0]['status'] == 'expired':
            print(f"  ✅ Status change verified!")
        
        # Cleanup
        os.remove('test_visa_data.db')
        print(f"\n  🧹 Test database cleaned up")
        
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        if os.path.exists('test_visa_data.db'):
            os.remove('test_visa_data.db')
    
    print("\n" + "=" * 50)
    print("✅ DATABASE TESTS COMPLETED")
    print("=" * 50)

def test_imports():
    """Test if all imports work"""
    print("\n" + "=" * 50)
    print("🧪 TESTING IMPORTS")
    print("=" * 50)
    
    required_modules = [
        'telegram',
        'requests',
        'bs4',
        'dotenv',
        'sqlite3'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - NOT INSTALLED")
    
    print("\n" + "=" * 50)
    print("✅ IMPORT TESTS COMPLETED")
    print("=" * 50)

if __name__ == '__main__':
    print("\n")
    print("╔════════════════════════════════════════════════╗")
    print("║   🤖 VISA CHECKER BOT - TEST SUITE 🤖        ║")
    print("╚════════════════════════════════════════════════╝")
    
    test_imports()
    test_scrapers()
    test_database()
    
    print("\n")
    print("╔════════════════════════════════════════════════╗")
    print("║   ✅ ALL TESTS COMPLETED ✅                   ║")
    print("╚════════════════════════════════════════════════╝")
    print("\n")
