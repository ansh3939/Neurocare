import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database configuration
DATABASE_URL = "sqlite:///healthcare.db"
DATABASE_PATH = BASE_DIR / "healthcare.db"

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Sensor thresholds for alerts
HEALTH_THRESHOLDS = {
    "heart_rate": {"min": 60, "max": 100},
    "blood_pressure_systolic": {"min": 90, "max": 140},
    "blood_pressure_diastolic": {"min": 60, "max": 90},
    "glucose": {"min": 70, "max": 140},
    "oxygen_saturation": {"min": 95, "max": 100},
    "temperature": {"min": 36.1, "max": 37.2}
}

# Federated Learning configuration
FL_CONFIG = {
    "num_rounds": 10,
    "local_epochs": 5,
    "batch_size": 32,
    "learning_rate": 0.001,
    "sequence_length": 24  # hours of data for LSTM/GRU
}

# MQTT configuration for sensor simulation
MQTT_CONFIG = {
    "broker": "localhost",
    "port": 1883,
    "keepalive": 60,
    "topics": {
        "heart_rate": "sensors/heart_rate",
        "blood_pressure": "sensors/blood_pressure",
        "glucose": "sensors/glucose",
        "oxygen": "sensors/oxygen",
        "temperature": "sensors/temperature"
    }
}

# File upload configuration
UPLOAD_FOLDER = BASE_DIR / "uploads"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'csv', 'json'}

# Create necessary directories
UPLOAD_FOLDER.mkdir(exist_ok=True)