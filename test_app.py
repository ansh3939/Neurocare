#!/usr/bin/env python3
"""
Test script for the Healthcare Federated Learning Application
"""

import sys
import os
import sqlite3
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import tensorflow
        print("✅ TensorFlow imported successfully")
    except ImportError as e:
        print(f"❌ TensorFlow import failed: {e}")
        return False
    
    try:
        import sklearn
        print("✅ Scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ Scikit-learn import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database operations"""
    print("\n🗄️ Testing database operations...")
    
    try:
        from database import db
        
        # Test user creation
        test_user = db.create_user(
            username="test_user",
            password_hash="test_hash",
            role="patient",
            email="test@example.com",
            full_name="Test User"
        )
        
        if test_user:
            print("✅ User creation successful")
        else:
            print("❌ User creation failed")
            return False
        
        # Test user retrieval
        user = db.get_user_by_id(1)
        if user:
            print("✅ User retrieval successful")
        else:
            print("❌ User retrieval failed")
            return False
        
        # Clean up test user
        # Note: In a real app, you'd have a delete method
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_ml_models():
    """Test machine learning models"""
    print("\n🧠 Testing machine learning models...")
    
    try:
        from ml_models import HealthPredictor, simulate_health_data
        
        # Test data simulation
        sample_data = simulate_health_data(hours=6)
        if not sample_data.empty:
            print("✅ Health data simulation successful")
        else:
            print("❌ Health data simulation failed")
            return False
        
        # Test predictor creation
        predictor = HealthPredictor("lstm")
        if predictor:
            print("✅ Health predictor creation successful")
        else:
            print("❌ Health predictor creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ML models test failed: {e}")
        return False

def test_sensor_simulator():
    """Test sensor simulator"""
    print("\n📡 Testing sensor simulator...")
    
    try:
        from sensor_simulator import SensorSimulator, HealthSensor
        
        # Test sensor creation
        simulator = SensorSimulator()
        simulator.add_patient_sensors(patient_id=1)
        
        if len(simulator.sensors) > 0:
            print("✅ Sensor simulator creation successful")
        else:
            print("❌ Sensor simulator creation failed")
            return False
        
        # Test sensor data generation
        sensor_data = simulator.get_current_values(patient_id=1)
        if sensor_data:
            print("✅ Sensor data generation successful")
        else:
            print("❌ Sensor data generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Sensor simulator test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import HEALTH_THRESHOLDS, FL_CONFIG, MQTT_CONFIG
        
        if HEALTH_THRESHOLDS and FL_CONFIG and MQTT_CONFIG:
            print("✅ Configuration loading successful")
            print(f"   - Health thresholds: {len(HEALTH_THRESHOLDS)} parameters")
            print(f"   - FL config: {len(FL_CONFIG)} settings")
            print(f"   - MQTT config: {len(MQTT_CONFIG)} settings")
        else:
            print("❌ Configuration loading failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "app.py",
        "config.py",
        "database.py",
        "auth.py",
        "ml_models.py",
        "sensor_simulator.py",
        "requirements.txt",
        "README.md",
        "pages/dashboard.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ All required files present")
        return True
    else:
        print(f"❌ Missing files: {missing_files}")
        return False

def main():
    """Run all tests"""
    print("🏥 Healthcare Federated Learning Application - Test Suite")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration", test_config),
        ("Module Imports", test_imports),
        ("Database", test_database),
        ("ML Models", test_ml_models),
        ("Sensor Simulator", test_sensor_simulator),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application, run:")
        print("  streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())