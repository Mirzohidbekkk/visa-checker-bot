"""
Database module for visa checker bot
Handles all database operations with SQLite
"""
import sqlite3
from datetime import datetime, timedelta
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class VisaDatabase:
    """Database handler for visa information"""
    
    def __init__(self, db_path: str = 'visa_data.db'):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER UNIQUE NOT NULL,
                        full_name TEXT NOT NULL,
                        passport_number TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create visas table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS visas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        country TEXT NOT NULL,
                        visa_type TEXT NOT NULL,
                        issue_date TEXT,
                        expiry_date TEXT NOT NULL,
                        days_remaining INTEGER,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                ''')
                
                # Create status history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS status_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        visa_id INTEGER NOT NULL,
                        old_status TEXT,
                        new_status TEXT NOT NULL,
                        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (visa_id) REFERENCES visas(id) ON DELETE CASCADE
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_telegram_id ON users(telegram_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_visa_user_id ON visas(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_visa_status ON visas(status)')
                
                conn.commit()
                logger.info(f"Database initialized: {self.db_path}")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def add_user(self, telegram_id: int, full_name: str, passport_number: str) -> int:
        """
        Add or update user in database
        
        Args:
            telegram_id: Telegram user ID
            full_name: User's full name
            passport_number: User's passport number
            
        Returns:
            User ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing user
                    cursor.execute('''
                        UPDATE users 
                        SET full_name = ?, passport_number = ?, updated_at = ?
                        WHERE telegram_id = ?
                    ''', (full_name, passport_number, datetime.now(), telegram_id))
                    user_id = existing[0]
                    logger.info(f"User {telegram_id} updated")
                else:
                    # Create new user
                    cursor.execute('''
                        INSERT INTO users (telegram_id, full_name, passport_number)
                        VALUES (?, ?, ?)
                    ''', (telegram_id, full_name, passport_number))
                    user_id = cursor.lastrowid
                    logger.info(f"User {telegram_id} created with ID {user_id}")
                
                conn.commit()
                return user_id
                
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            raise
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """
        Get user by telegram ID
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User dictionary or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
                result = cursor.fetchone()
                
                if result:
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    def add_visa(self, user_id: int, country: str, visa_type: str, 
                 issue_date: str, expiry_date: str) -> int:
        """
        Add visa record for user
        
        Args:
            user_id: User ID
            country: Country name
            visa_type: Type of visa
            issue_date: Issue date (DD.MM.YYYY)
            expiry_date: Expiry date (DD.MM.YYYY)
            
        Returns:
            Visa ID
        """
        try:
            days_remaining = self._calculate_days_remaining(expiry_date)
            status = 'expired' if days_remaining <= 0 else 'active'
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO visas 
                    (user_id, country, visa_type, issue_date, expiry_date, days_remaining, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, country, visa_type, issue_date, expiry_date, days_remaining, status))
                
                visa_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Visa {visa_id} added for user {user_id} - {country}")
                return visa_id
                
        except Exception as e:
            logger.error(f"Error adding visa: {str(e)}")
            raise
    
    def get_user_visas(self, user_id: int) -> List[Dict]:
        """
        Get all visas for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of visa dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM visas 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Error getting user visas: {str(e)}")
            return []
    
    def update_visa_status(self, visa_id: int, new_status: str) -> bool:
        """
        Update visa status and record history
        
        Args:
            visa_id: Visa ID
            new_status: New status (active, expired, etc.)
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current status
                cursor.execute('SELECT status FROM visas WHERE id = ?', (visa_id,))
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"Visa {visa_id} not found")
                    return False
                
                old_status = result[0]
                
                # Update status
                cursor.execute('''
                    UPDATE visas 
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                ''', (new_status, datetime.now(), visa_id))
                
                # Record history
                cursor.execute('''
                    INSERT INTO status_history (visa_id, old_status, new_status)
                    VALUES (?, ?, ?)
                ''', (visa_id, old_status, new_status))
                
                conn.commit()
                logger.info(f"Visa {visa_id} status updated: {old_status} -> {new_status}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating visa status: {str(e)}")
            return False
    
    def get_expiring_visas(self, days_before: int = 7) -> List[Dict]:
        """
        Get visas expiring within specified days
        
        Args:
            days_before: Number of days to check ahead
            
        Returns:
            List of expiring visa dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM visas 
                    WHERE status = 'active' AND days_remaining <= ?
                    ORDER BY days_remaining ASC
                ''', (days_before,))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"Error getting expiring visas: {str(e)}")
            return []
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete user and all associated visas
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete visas (cascade delete)
                cursor.execute('DELETE FROM visas WHERE user_id = ?', (user_id,))
                
                # Delete user
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                
                conn.commit()
                logger.info(f"User {user_id} deleted with all associated data")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
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
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM users')
                total_users = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM visas')
                total_visas = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM visas WHERE status = 'active'")
                active_visas = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM visas WHERE status = 'expired'")
                expired_visas = cursor.fetchone()[0]
                
                return {
                    'total_users': total_users,
                    'total_visas': total_visas,
                    'active_visas': active_visas,
                    'expired_visas': expired_visas
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
