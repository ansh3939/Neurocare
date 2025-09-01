import streamlit as st
from auth import login_page, create_sample_users
from database import db
import os

# Page configuration
st.set_page_config(
    page_title="Smarter Healthcare with Federated Learning",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Sidebar
    with st.sidebar:
        st.title("🏥 Healthcare System")
        st.markdown("---")
        
        # Sample data creation (for testing)
        if st.button("🔧 Create Sample Users"):
            create_sample_users()
        
        st.markdown("---")
        st.markdown("**Features:**")
        st.markdown("• 🔐 User Authentication")
        st.markdown("• 📊 Real-time Monitoring")
        st.markdown("• 🧠 AI Predictions")
        st.markdown("• 🌐 Federated Learning")
        st.markdown("• 📈 Health Analytics")
        st.markdown("• 🚨 Smart Alerts")
        
        st.markdown("---")
        st.markdown("**Sample Credentials:**")
        st.markdown("Patient: `patient1` / `password123`")
        st.markdown("Doctor: `doctor1` / `password123`")
    
    # Main content
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    
    # Page routing
    if st.session_state.current_page == 'login':
        login_page()
        
        # Check if user is authenticated and redirect
        from auth import auth
        if auth.is_authenticated():
            st.session_state.current_page = 'dashboard'
            st.rerun()
    
    elif st.session_state.current_page == 'dashboard':
        # Import and show dashboard
        from pages.dashboard import main as dashboard_main
        dashboard_main()

if __name__ == "__main__":
    main()
