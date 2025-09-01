import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import pandas as pd
import numpy as np
import streamlit as st
from config import HEALTH_THRESHOLDS, MQTT_CONFIG

class HealthSensor:
    def __init__(self, sensor_type: str, patient_id: int):
        self.sensor_type = sensor_type
        self.patient_id = patient_id
        self.current_value = self._get_normal_value()
        self.trend = 0
        self.noise_level = 0.1
        self.last_update = datetime.now()
        
    def _get_normal_value(self) -> float:
        """Get normal baseline value for sensor type"""
        baselines = {
            'heart_rate': 75,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'glucose': 100,
            'oxygen_saturation': 98,
            'temperature': 36.8
        }
        return baselines.get(self.sensor_type, 0)
    
    def _get_variation_range(self) -> float:
        """Get normal variation range for sensor type"""
        variations = {
            'heart_rate': 15,
            'blood_pressure_systolic': 20,
            'blood_pressure_diastolic': 10,
            'glucose': 30,
            'oxygen_saturation': 2,
            'temperature': 0.5
        }
        return variations.get(self.sensor_type, 5)
    
    def update_value(self) -> Dict:
        """Update sensor value with realistic variations"""
        now = datetime.now()
        time_diff = (now - self.last_update).total_seconds() / 3600  # hours
        
        # Add trend (slow drift)
        self.trend += random.uniform(-0.01, 0.01)
        self.trend = np.clip(self.trend, -0.1, 0.1)
        
        # Add noise
        noise = random.uniform(-self.noise_level, self.noise_level)
        
        # Calculate new value
        variation_range = self._get_variation_range()
        new_value = self.current_value + self.trend + noise * variation_range
        
        # Ensure value stays within realistic bounds
        min_val = HEALTH_THRESHOLDS[self.sensor_type]['min']
        max_val = HEALTH_THRESHOLDS[self.sensor_type]['max']
        new_value = np.clip(new_value, min_val, max_val)
        
        self.current_value = new_value
        self.last_update = now
        
        return {
            'sensor_type': self.sensor_type,
            'patient_id': self.patient_id,
            'value': round(new_value, 2),
            'timestamp': now.isoformat(),
            'status': self._get_status(new_value)
        }
    
    def _get_status(self, value: float) -> str:
        """Get status based on thresholds"""
        min_val = HEALTH_THRESHOLDS[self.sensor_type]['min']
        max_val = HEALTH_THRESHOLDS[self.sensor_type]['max']
        
        if value < min_val or value > max_val:
            return 'alert'
        elif abs(value - (min_val + max_val) / 2) > (max_val - min_val) * 0.3:
            return 'warning'
        else:
            return 'normal'

class SensorSimulator:
    def __init__(self):
        self.sensors: Dict[str, HealthSensor] = {}
        self.is_running = False
        self.update_interval = 1.0  # seconds
        self.data_callback: Optional[Callable] = None
        self.alert_callback: Optional[Callable] = None
        
    def add_patient_sensors(self, patient_id: int):
        """Add all sensors for a patient"""
        sensor_types = [
            'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'glucose', 'oxygen_saturation', 'temperature'
        ]
        
        for sensor_type in sensor_types:
            key = f"{patient_id}_{sensor_type}"
            self.sensors[key] = HealthSensor(sensor_type, patient_id)
    
    def remove_patient_sensors(self, patient_id: int):
        """Remove all sensors for a patient"""
        keys_to_remove = [key for key in self.sensors.keys() if key.startswith(f"{patient_id}_")]
        for key in keys_to_remove:
            del self.sensors[key]
    
    def set_data_callback(self, callback: Callable):
        """Set callback for sensor data updates"""
        self.data_callback = callback
    
    def set_alert_callback(self, callback: Callable):
        """Set callback for sensor alerts"""
        self.alert_callback = callback
    
    def start_simulation(self):
        """Start sensor simulation"""
        self.is_running = True
        asyncio.create_task(self._simulation_loop())
    
    def stop_simulation(self):
        """Stop sensor simulation"""
        self.is_running = False
    
    async def _simulation_loop(self):
        """Main simulation loop"""
        while self.is_running:
            for sensor in self.sensors.values():
                data = sensor.update_value()
                
                # Call data callback if set
                if self.data_callback:
                    self.data_callback(data)
                
                # Check for alerts
                if data['status'] in ['alert', 'warning'] and self.alert_callback:
                    self.alert_callback(data)
            
            await asyncio.sleep(self.update_interval)
    
    def get_current_values(self, patient_id: int) -> Dict[str, Dict]:
        """Get current values for all sensors of a patient"""
        patient_sensors = {}
        for key, sensor in self.sensors.items():
            if key.startswith(f"{patient_id}_"):
                sensor_type = sensor.sensor_type
                patient_sensors[sensor_type] = sensor.update_value()
        return patient_sensors
    
    def simulate_anomaly(self, patient_id: int, sensor_type: str, duration_minutes: int = 5):
        """Simulate an anomaly for testing"""
        key = f"{patient_id}_{sensor_type}"
        if key in self.sensors:
            sensor = self.sensors[key]
            
            # Temporarily modify sensor behavior
            original_noise = sensor.noise_level
            sensor.noise_level = 0.5  # Increase noise
            
            # Schedule restoration
            async def restore_sensor():
                await asyncio.sleep(duration_minutes * 60)
                sensor.noise_level = original_noise
            
            asyncio.create_task(restore_sensor())

class MockMQTTClient:
    """Mock MQTT client for sensor data simulation"""
    def __init__(self):
        self.connected = False
        self.subscribers = {}
        self.published_messages = []
    
    def connect(self, broker: str, port: int = 1883):
        """Mock connection to MQTT broker"""
        self.connected = True
        return True
    
    def disconnect(self):
        """Mock disconnection from MQTT broker"""
        self.connected = False
    
    def publish(self, topic: str, payload: str):
        """Mock publishing to MQTT topic"""
        if self.connected:
            message = {
                'topic': topic,
                'payload': payload,
                'timestamp': datetime.now().isoformat()
            }
            self.published_messages.append(message)
            
            # Notify subscribers
            if topic in self.subscribers:
                for callback in self.subscribers[topic]:
                    callback(payload)
    
    def subscribe(self, topic: str, callback: Callable):
        """Mock subscription to MQTT topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
    
    def is_connected(self) -> bool:
        """Check if connected to MQTT broker"""
        return self.connected

class WebSocketSimulator:
    """WebSocket simulator for real-time communication"""
    def __init__(self):
        self.connections = {}
        self.message_handlers = {}
    
    def add_connection(self, connection_id: str, send_callback: Callable):
        """Add a new WebSocket connection"""
        self.connections[connection_id] = send_callback
    
    def remove_connection(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
    
    def broadcast_message(self, message: Dict):
        """Broadcast message to all connections"""
        for connection_id, send_callback in self.connections.items():
            try:
                send_callback(message)
            except Exception as e:
                st.error(f"Error sending message to {connection_id}: {e}")
    
    def send_to_connection(self, connection_id: str, message: Dict):
        """Send message to specific connection"""
        if connection_id in self.connections:
            try:
                self.connections[connection_id](message)
            except Exception as e:
                st.error(f"Error sending message to {connection_id}: {e}")

# Global instances
sensor_simulator = SensorSimulator()
mqtt_client = MockMQTTClient()
websocket_simulator = WebSocketSimulator()

def generate_sample_csv_data(patient_id: int, hours: int = 24) -> str:
    """Generate sample CSV data for testing"""
    # Create sample data
    timestamps = pd.date_range(
        start=datetime.now() - timedelta(hours=hours),
        end=datetime.now(),
        freq='H'
    )
    
    data = []
    for ts in timestamps:
        row = {
            'timestamp': ts.isoformat(),
            'patient_id': patient_id,
            'heart_rate': random.randint(60, 100),
            'blood_pressure_systolic': random.randint(90, 140),
            'blood_pressure_diastolic': random.randint(60, 90),
            'glucose': random.uniform(70, 140),
            'oxygen_saturation': random.uniform(95, 100),
            'temperature': random.uniform(36.1, 37.2)
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def parse_health_csv(csv_content: str) -> pd.DataFrame:
    """Parse uploaded CSV health data"""
    try:
        df = pd.read_csv(csv_content)
        
        # Validate required columns
        required_columns = [
            'timestamp', 'heart_rate', 'blood_pressure_systolic', 
            'blood_pressure_diastolic', 'glucose', 'oxygen_saturation', 'temperature'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            return pd.DataFrame()
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        return df
        
    except Exception as e:
        st.error(f"Error parsing CSV: {e}")
        return pd.DataFrame()

def check_health_alerts(health_data: Dict) -> Optional[Dict]:
    """Check if health data triggers any alerts"""
    sensor_type = health_data['sensor_type']
    value = health_data['value']
    
    if sensor_type in HEALTH_THRESHOLDS:
        min_val = HEALTH_THRESHOLDS[sensor_type]['min']
        max_val = HEALTH_THRESHOLDS[sensor_type]['max']
        
        if value < min_val or value > max_val:
            severity = 'critical' if abs(value - (min_val + max_val) / 2) > (max_val - min_val) * 0.5 else 'high'
            
            return {
                'type': 'health_threshold',
                'sensor': sensor_type,
                'value': value,
                'threshold_min': min_val,
                'threshold_max': max_val,
                'severity': severity,
                'message': f"{sensor_type.replace('_', ' ').title()}: {value} (Normal: {min_val}-{max_val})"
            }
    
    return None