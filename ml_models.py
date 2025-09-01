import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import json
from typing import Dict, List, Tuple, Optional
import streamlit as st
from config import FL_CONFIG

class HealthPredictor:
    def __init__(self, model_type: str = "lstm"):
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler()
        self.sequence_length = FL_CONFIG["sequence_length"]
        self.feature_columns = [
            'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'glucose', 'oxygen_saturation', 'temperature'
        ]
    
    def create_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """Create LSTM or GRU model"""
        if self.model_type == "lstm":
            model = keras.Sequential([
                layers.LSTM(64, return_sequences=True, input_shape=input_shape),
                layers.Dropout(0.2),
                layers.LSTM(32, return_sequences=False),
                layers.Dropout(0.2),
                layers.Dense(16, activation='relu'),
                layers.Dense(len(self.feature_columns), activation='linear')
            ])
        else:  # GRU
            model = keras.Sequential([
                layers.GRU(64, return_sequences=True, input_shape=input_shape),
                layers.Dropout(0.2),
                layers.GRU(32, return_sequences=False),
                layers.Dropout(0.2),
                layers.Dense(16, activation='relu'),
                layers.Dense(len(self.feature_columns), activation='linear')
            ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=FL_CONFIG["learning_rate"]),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for LSTM/GRU training"""
        # Fill missing values with forward fill
        df = df[self.feature_columns].fillna(method='ffill').fillna(method='bfill')
        
        # Normalize data
        scaled_data = self.scaler.fit_transform(df)
        
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i])
            y.append(scaled_data[i])
        
        return np.array(X), np.array(y)
    
    def train_model(self, df: pd.DataFrame, epochs: int = None) -> Dict:
        """Train the model on patient data"""
        if df.empty or len(df) < self.sequence_length + 1:
            return {"error": "Insufficient data for training"}
        
        # Prepare data
        X, y = self.prepare_data(df)
        
        if len(X) == 0:
            return {"error": "No valid sequences found"}
        
        # Create and train model
        input_shape = (X.shape[1], X.shape[2])
        self.model = self.create_model(input_shape)
        
        epochs = epochs or FL_CONFIG["local_epochs"]
        
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=FL_CONFIG["batch_size"],
            validation_split=0.2,
            verbose=0
        )
        
        # Evaluate model
        val_loss = history.history['val_loss'][-1]
        val_mae = history.history['val_mae'][-1]
        
        return {
            "loss": val_loss,
            "mae": val_mae,
            "epochs_trained": epochs,
            "samples_used": len(X)
        }
    
    def predict_next_values(self, recent_data: pd.DataFrame) -> Dict:
        """Predict next health values"""
        if self.model is None:
            return {"error": "Model not trained"}
        
        if len(recent_data) < self.sequence_length:
            return {"error": f"Insufficient data. Need at least {self.sequence_length} records"}
        
        # Prepare recent data
        recent_scaled = self.scaler.transform(recent_data[self.feature_columns].tail(self.sequence_length))
        X = recent_scaled.reshape(1, self.sequence_length, len(self.feature_columns))
        
        # Make prediction
        prediction_scaled = self.model.predict(X, verbose=0)
        prediction = self.scaler.inverse_transform(prediction_scaled)
        
        # Convert to readable format
        result = {}
        for i, col in enumerate(self.feature_columns):
            result[col] = float(prediction[0][i])
        
        return result
    
    def get_model_weights(self) -> str:
        """Get model weights as JSON string for federated learning"""
        if self.model is None:
            return ""
        
        weights = []
        for layer in self.model.layers:
            if layer.weights:
                layer_weights = []
                for weight in layer.weights:
                    layer_weights.append(weight.numpy().tolist())
                weights.append(layer_weights)
        
        return json.dumps(weights)
    
    def set_model_weights(self, weights_json: str):
        """Set model weights from JSON string (for federated learning)"""
        if not weights_json:
            return
        
        try:
            weights = json.loads(weights_json)
            
            # Create model if it doesn't exist
            if self.model is None:
                input_shape = (self.sequence_length, len(self.feature_columns))
                self.model = self.create_model(input_shape)
            
            # Set weights
            weight_idx = 0
            for layer in self.model.layers:
                if layer.weights:
                    layer_weights = weights[weight_idx]
                    for i, weight in enumerate(layer_weights):
                        layer.weights[i].assign(tf.constant(weight))
                    weight_idx += 1
                    
        except Exception as e:
            st.error(f"Error setting model weights: {e}")

class FederatedLearningManager:
    def __init__(self):
        self.global_model = None
        self.participating_clients = []
        self.training_rounds = []
    
    def initialize_global_model(self, model_type: str = "lstm"):
        """Initialize global model for federated learning"""
        predictor = HealthPredictor(model_type)
        # Create a dummy model to get the structure
        dummy_data = pd.DataFrame({
            'heart_rate': [70] * 25,
            'blood_pressure_systolic': [120] * 25,
            'blood_pressure_diastolic': [80] * 25,
            'glucose': [100] * 25,
            'oxygen_saturation': [98] * 25,
            'temperature': [36.8] * 25
        })
        
        predictor.train_model(dummy_data, epochs=1)
        self.global_model = predictor
        return predictor
    
    def aggregate_models(self, client_models: List[HealthPredictor]) -> HealthPredictor:
        """Aggregate client models using federated averaging"""
        if not client_models:
            return self.global_model
        
        # Get weights from all clients
        all_weights = []
        for client in client_models:
            if client.model is not None:
                weights = []
                for layer in client.model.layers:
                    if layer.weights:
                        layer_weights = []
                        for weight in layer.weights:
                            layer_weights.append(weight.numpy())
                        weights.append(layer_weights)
                all_weights.append(weights)
        
        if not all_weights:
            return self.global_model
        
        # Average the weights
        averaged_weights = []
        for layer_idx in range(len(all_weights[0])):
            layer_weights = []
            for weight_idx in range(len(all_weights[0][layer_idx])):
                # Stack weights from all clients
                stacked = np.stack([client_weights[layer_idx][weight_idx] 
                                  for client_weights in all_weights])
                # Average
                averaged = np.mean(stacked, axis=0)
                layer_weights.append(averaged)
            averaged_weights.append(layer_weights)
        
        # Set averaged weights to global model
        weights_json = json.dumps(averaged_weights)
        self.global_model.set_model_weights(weights_json)
        
        return self.global_model
    
    def train_federated_round(self, client_data: List[pd.DataFrame], 
                            model_type: str = "lstm") -> Dict:
        """Execute one round of federated learning"""
        if not client_data:
            return {"error": "No client data provided"}
        
        # Initialize global model if needed
        if self.global_model is None:
            self.initialize_global_model(model_type)
        
        # Train local models on each client
        client_models = []
        training_results = []
        
        for i, data in enumerate(client_data):
            if len(data) > FL_CONFIG["sequence_length"]:
                client = HealthPredictor(model_type)
                result = client.train_model(data, epochs=FL_CONFIG["local_epochs"])
                if "error" not in result:
                    client_models.append(client)
                    training_results.append(result)
        
        if not client_models:
            return {"error": "No valid models trained"}
        
        # Aggregate models
        self.global_model = self.aggregate_models(client_models)
        
        # Calculate average metrics
        avg_loss = np.mean([r["loss"] for r in training_results])
        avg_mae = np.mean([r["mae"] for r in training_results])
        
        round_result = {
            "round": len(self.training_rounds) + 1,
            "clients_participated": len(client_models),
            "avg_loss": avg_loss,
            "avg_mae": avg_mae,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        self.training_rounds.append(round_result)
        
        return round_result
    
    def get_training_progress(self) -> pd.DataFrame:
        """Get federated learning training progress"""
        if not self.training_rounds:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.training_rounds)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

# Global instances
health_predictor = HealthPredictor()
fl_manager = FederatedLearningManager()

def simulate_health_data(hours: int = 24) -> pd.DataFrame:
    """Simulate realistic health sensor data"""
    np.random.seed(42)  # For reproducible results
    
    timestamps = pd.date_range(
        start=pd.Timestamp.now() - pd.Timedelta(hours=hours),
        end=pd.Timestamp.now(),
        freq='H'
    )
    
    # Base values with realistic variations
    base_values = {
        'heart_rate': 75,
        'blood_pressure_systolic': 120,
        'blood_pressure_diastolic': 80,
        'glucose': 100,
        'oxygen_saturation': 98,
        'temperature': 36.8
    }
    
    # Variations
    variations = {
        'heart_rate': 15,
        'blood_pressure_systolic': 20,
        'blood_pressure_diastolic': 10,
        'glucose': 30,
        'oxygen_saturation': 2,
        'temperature': 0.5
    }
    
    data = {}
    for metric, base in base_values.items():
        # Add some trend and noise
        trend = np.linspace(0, np.random.normal(0, 0.1), len(timestamps))
        noise = np.random.normal(0, variations[metric] * 0.1, len(timestamps))
        
        values = base + trend + noise
        
        # Ensure values stay within realistic bounds
        if metric == 'heart_rate':
            values = np.clip(values, 50, 120)
        elif metric == 'blood_pressure_systolic':
            values = np.clip(values, 80, 160)
        elif metric == 'blood_pressure_diastolic':
            values = np.clip(values, 50, 100)
        elif metric == 'glucose':
            values = np.clip(values, 60, 200)
        elif metric == 'oxygen_saturation':
            values = np.clip(values, 90, 100)
        elif metric == 'temperature':
            values = np.clip(values, 35.5, 38.0)
        
        data[metric] = values
    
    df = pd.DataFrame(data, index=timestamps)
    df.index.name = 'timestamp'
    
    return df