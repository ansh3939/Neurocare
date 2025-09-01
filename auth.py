import streamlit as st
import bcrypt
import hashlib
from typing import Optional, Dict
from database import db

class AuthManager:
    def __init__(self):
        self.session_key = "user_session"
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_hash(self, text: str) -> str:
        """Create a simple hash for session management"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def login_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        # First get user by username
        conn = db.db_path
        import sqlite3
        conn = sqlite3.connect(conn)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, role, email, full_name
            FROM users
            WHERE username = ?
        ''', (username,))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and self.verify_password(password, user_data[2]):
            # Create session
            session_data = {
                'user_id': user_data[0],
                'username': user_data[1],
                'role': user_data[3],
                'full_name': user_data[5],
                'email': user_data[4]
            }
            st.session_state[self.session_key] = session_data
            return session_data
        return None
    
    def register_user(self, username: str, password: str, email: str, full_name: str, role: str) -> bool:
        """Register a new user"""
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user in database
        success = db.create_user(username, password_hash, role, email, full_name)
        return success
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.session_key in st.session_state
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user"""
        if self.is_authenticated():
            return st.session_state[self.session_key]
        return None
    
    def logout_user(self):
        """Logout current user"""
        if self.session_key in st.session_state:
            del st.session_state[self.session_key]
    
    def require_auth(self, role: str = None):
        """Decorator to require authentication and optionally specific role"""
        if not self.is_authenticated():
            st.error("Please login to access this page.")
            st.stop()
        
        if role and self.get_current_user()['role'] != role:
            st.error(f"Access denied. {role.capitalize()} role required.")
            st.stop()

# Global auth manager instance
auth = AuthManager()

def login_page():
    """Login page UI"""
    st.title("🔐 Healthcare System Login")
    
    # Check if already logged in
    if auth.is_authenticated():
        st.success(f"Welcome back, {auth.get_current_user()['full_name']}!")
        if st.button("Go to Dashboard"):
            st.switch_page("pages/dashboard.py")
        return
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                user = auth.login_user(username, password)
                if user:
                    st.success(f"Welcome, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please fill in all fields")
    
    # Signup link
    st.markdown("---")
    st.markdown("Don't have an account? [Sign up here](#signup)")
    
    # Signup form (collapsible)
    with st.expander("Create New Account"):
        with st.form("signup_form"):
            st.subheader("Sign Up")
            
            new_username = st.text_input("Username", key="signup_username")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            new_email = st.text_input("Email", key="signup_email")
            new_full_name = st.text_input("Full Name", key="signup_fullname")
            new_role = st.selectbox("Role", ["patient", "doctor"], key="signup_role")
            
            signup_button = st.form_submit_button("Sign Up")
            
            if signup_button:
                if not all([new_username, new_password, confirm_password, new_email, new_full_name]):
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    success = auth.register_user(new_username, new_password, new_email, new_full_name, new_role)
                    if success:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username or email already exists")

def create_sample_users():
    """Create sample users for testing"""
    # Sample patient
    auth.register_user("patient1", "password123", "patient1@health.com", "John Doe", "patient")
    
    # Sample doctor
    auth.register_user("doctor1", "password123", "doctor1@health.com", "Dr. Smith", "doctor")
    
    # Sample patient with profile
    auth.register_user("patient2", "password123", "patient2@health.com", "Jane Smith", "patient")
    
    st.success("Sample users created successfully!")
    st.info("Username: patient1/doctor1, Password: password123")