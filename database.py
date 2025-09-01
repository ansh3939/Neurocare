import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
from config import DATABASE_PATH

class HealthcareDatabase:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('patient', 'doctor')),
                email TEXT UNIQUE,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Patient profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                age INTEGER,
                gender TEXT,
                weight REAL,
                height REAL,
                medical_history TEXT,
                emergency_contact TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Health records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                heart_rate INTEGER,
                blood_pressure_systolic INTEGER,
                blood_pressure_diastolic INTEGER,
                glucose REAL,
                oxygen_saturation REAL,
                temperature REAL,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES users (id)
            )
        ''')
        
        # Federated learning models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fl_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                model_type TEXT NOT NULL CHECK (model_type IN ('lstm', 'gru')),
                model_weights TEXT,  # JSON string of model weights
                accuracy REAL,
                loss REAL,
                training_round INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users (id)
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, password_hash: str, role: str, email: str, full_name: str) -> bool:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, email, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, role, email, full_name))
            
            user_id = cursor.lastrowid
            
            # Create patient profile if role is patient
            if role == 'patient':
                cursor.execute('''
                    INSERT INTO patient_profiles (user_id)
                    VALUES (?)
                ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username: str, password_hash: str) -> Optional[Dict]:
        """Authenticate user and return user info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, role, email, full_name
            FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'email': user[3],
                'full_name': user[4]
            }
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, role, email, full_name
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'email': user[3],
                'full_name': user[4]
            }
        return None
    
    def get_all_patients(self) -> List[Dict]:
        """Get all patients for doctor dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.full_name, u.email, p.age, p.gender
            FROM users u
            LEFT JOIN patient_profiles p ON u.id = p.user_id
            WHERE u.role = 'patient'
        ''')
        
        patients = []
        for row in cursor.fetchall():
            patients.append({
                'id': row[0],
                'username': row[1],
                'full_name': row[2],
                'email': row[3],
                'age': row[4],
                'gender': row[5]
            })
        
        conn.close()
        return patients
    
    def add_health_record(self, patient_id: int, health_data: Dict) -> bool:
        """Add a new health record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO health_records 
                (patient_id, heart_rate, blood_pressure_systolic, blood_pressure_diastolic, 
                 glucose, oxygen_saturation, temperature, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                health_data.get('heart_rate'),
                health_data.get('blood_pressure_systolic'),
                health_data.get('blood_pressure_diastolic'),
                health_data.get('glucose'),
                health_data.get('oxygen_saturation'),
                health_data.get('temperature'),
                health_data.get('notes', '')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding health record: {e}")
            return False
    
    def get_patient_health_records(self, patient_id: int, hours: int = 24) -> pd.DataFrame:
        """Get patient health records for the last N hours"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT timestamp, heart_rate, blood_pressure_systolic, blood_pressure_diastolic,
                   glucose, oxygen_saturation, temperature, notes
            FROM health_records
            WHERE patient_id = ? AND timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp ASC
        '''.format(hours)
        
        df = pd.read_sql_query(query, conn, params=(patient_id,))
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def save_fl_model(self, patient_id: int, model_type: str, model_weights: str, 
                     accuracy: float, loss: float, training_round: int) -> bool:
        """Save federated learning model weights"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO fl_models (patient_id, model_type, model_weights, accuracy, loss, training_round)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, model_type, model_weights, accuracy, loss, training_round))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving FL model: {e}")
            return False
    
    def get_fl_models(self, patient_id: int, model_type: str = None) -> List[Dict]:
        """Get federated learning models for a patient"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if model_type:
            cursor.execute('''
                SELECT model_type, accuracy, loss, training_round, created_at
                FROM fl_models
                WHERE patient_id = ? AND model_type = ?
                ORDER BY training_round DESC
            ''', (patient_id, model_type))
        else:
            cursor.execute('''
                SELECT model_type, accuracy, loss, training_round, created_at
                FROM fl_models
                WHERE patient_id = ?
                ORDER BY training_round DESC
            ''', (patient_id,))
        
        models = []
        for row in cursor.fetchall():
            models.append({
                'model_type': row[0],
                'accuracy': row[1],
                'loss': row[2],
                'training_round': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return models
    
    def create_alert(self, patient_id: int, alert_type: str, message: str, severity: str) -> bool:
        """Create a new alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (patient_id, alert_type, message, severity)
                VALUES (?, ?, ?, ?)
            ''', (patient_id, alert_type, message, severity))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating alert: {e}")
            return False
    
    def get_patient_alerts(self, patient_id: int, unread_only: bool = False) -> List[Dict]:
        """Get alerts for a patient"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if unread_only:
            cursor.execute('''
                SELECT alert_type, message, severity, created_at
                FROM alerts
                WHERE patient_id = ? AND is_read = FALSE
                ORDER BY created_at DESC
            ''', (patient_id,))
        else:
            cursor.execute('''
                SELECT alert_type, message, severity, created_at, is_read
                FROM alerts
                WHERE patient_id = ?
                ORDER BY created_at DESC
            ''', (patient_id,))
        
        alerts = []
        for row in cursor.fetchall():
            if unread_only:
                alerts.append({
                    'alert_type': row[0],
                    'message': row[1],
                    'severity': row[2],
                    'created_at': row[3]
                })
            else:
                alerts.append({
                    'alert_type': row[0],
                    'message': row[1],
                    'severity': row[2],
                    'created_at': row[3],
                    'is_read': row[4]
                })
        
        conn.close()
        return alerts
    
    def mark_alert_read(self, alert_id: int) -> bool:
        """Mark an alert as read"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts
                SET is_read = TRUE
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking alert as read: {e}")
            return False

# Global database instance
db = HealthcareDatabase()