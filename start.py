#!/usr/bin/env python3
"""
Startup script for the Healthcare Federated Learning Application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    try:
        import pandas
        print("✅ Pandas is installed")
    except ImportError:
        print("❌ Pandas not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
    
    try:
        import plotly
        print("✅ Plotly is installed")
    except ImportError:
        print("❌ Plotly not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])

def install_requirements():
    """Install requirements from requirements.txt"""
    if Path("requirements.txt").exists():
        print("📦 Installing requirements...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    else:
        print("⚠️ requirements.txt not found")
    
    return True

def start_application():
    """Start the Streamlit application"""
    print("🚀 Starting Healthcare Application...")
    print("📱 The application will open in your default browser")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Tips:")
    print("   - Use the sidebar to create sample users")
    print("   - Login with patient1/password123 or doctor1/password123")
    print("   - Press Ctrl+C to stop the application")
    print("\n" + "="*50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def main():
    """Main startup function"""
    print("🏥 Healthcare Federated Learning Application")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Error: app.py not found in current directory")
        print("Please run this script from the project root directory")
        return 1
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return 1
    
    # Start application
    start_application()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())