"""
Database module for storing visa information
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class VisaDatabase:
    def __init__(self, db_path: str = "visa_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                full_name TEXT,
                passport_number TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Visa records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visas (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                country TEXT,
                visa_type TEXT,
                issue_date TEXT,
                expiry_date TEXT,
                days_remaining INTEGER,
                status TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Status history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY,
                visa_id INTEGER,
                old_status TEXT,
                new_status TEXT,
                changed_at TIMESTAMP,
                FOREIGN KEY (visa_id) REFERENCES visas(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, telegram_id: int, full_name: str, passport_number: str) -> int:
        """Add or update user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (telegram_id, full_name, passport_number, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, full_name, passport_number, datetime.now(), datetime.now()))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Get user by telegram ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, telegram_id, full_name, passport_number FROM users WHERE telegram_id = ?', 
                      (telegram_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'telegram_id': result[1],
                'full_name': result[2],
                'passport_number': result[3]
            }
        return None
    
    def add_visa(self, user_id: int, country: str, visa_type: str, 
                issue_date: str, expiry_date: str) -> int:
        """Add visa record"""
        from datetime import datetime as dt
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate days remaining
        expiry = dt.strptime(expiry_date, "%d.%m.%Y")
        days_remaining = (expiry - dt.now()).days
        
        cursor.execute('''
            INSERT INTO visas (user_id, country, visa_type, issue_date, expiry_date, 
                              days_remaining, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, country, visa_type, issue_date, expiry_date, 
              days_remaining, 'active', datetime.now(), datetime.now()))
        
        conn.commit()
        visa_id = cursor.lastrowid
        conn.close()
        return visa_id
    
    def get_user_visas(self, user_id: int) -> List[Dict]:
        """Get all visas for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, country, visa_type, issue_date, expiry_date, 
                   days_remaining, status FROM visas WHERE user_id = ?
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        visas = []
        for row in results:
            visas.append({
                'id': row[0],
                'country': row[1],
                'visa_type': row[2],
                'issue_date': row[3],
                'expiry_date': row[4],
                'days_remaining': row[5],
                'status': row[6]
            })
        return visas
    
    def update_visa_status(self, visa_id: int, new_status: str):
        """Update visa status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get old status
        cursor.execute('SELECT status FROM visas WHERE id = ?', (visa_id,))
        old_status = cursor.fetchone()[0]
        
        # Update visa
        cursor.execute('''
            UPDATE visas SET status = ?, updated_at = ? WHERE id = ?
        ''', (new_status, datetime.now(), visa_id))
        
        # Record history
        cursor.execute('''
            INSERT INTO status_history (visa_id, old_status, new_status, changed_at)
            VALUES (?, ?, ?, ?)
        ''', (visa_id, old_status, new_status, datetime.now()))
        
        conn.commit()
        conn.close()
  