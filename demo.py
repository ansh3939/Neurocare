#!/usr/bin/env python3
"""
Demo script for the Healthcare Federated Learning Application
This script demonstrates the key features without running the full Streamlit app.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def demo_health_data_simulation():
    """Demonstrate health data simulation"""
    print("📊 Health Data Simulation Demo")
    print("=" * 40)
    
    # Simulate 24 hours of health data
    timestamps = pd.date_range(
        start=datetime.now() - timedelta(hours=24),
        end=datetime.now(),
        freq='H'
    )
    
    # Generate realistic health data
    np.random.seed(42)  # For reproducible results
    
    heart_rate = np.random.normal(75, 10, len(timestamps))
    heart_rate = np.clip(heart_rate, 60, 100)
    
    blood_pressure_systolic = np.random.normal(120, 15, len(timestamps))
    blood_pressure_systolic = np.clip(blood_pressure_systolic, 90, 150)
    
    glucose = np.random.normal(100, 20, len(timestamps))
    glucose = np.clip(glucose, 70, 150)
    
    # Create DataFrame
    health_data = pd.DataFrame({
        'timestamp': timestamps,
        'heart_rate': heart_rate.round(1),
        'blood_pressure_systolic': blood_pressure_systolic.round(1),
        'glucose': glucose.round(1)
    })
    
    print("Sample health data (first 5 records):")
    print(health_data.head())
    
    print(f"\nData summary:")
    print(f"Total records: {len(health_data)}")
    print(f"Time range: {health_data['timestamp'].min()} to {health_data['timestamp'].max()}")
    print(f"Heart rate range: {health_data['heart_rate'].min():.1f} - {health_data['heart_rate'].max():.1f} bpm")
    print(f"Blood pressure range: {health_data['blood_pressure_systolic'].min():.1f} - {health_data['blood_pressure_systolic'].max():.1f} mmHg")
    print(f"Glucose range: {health_data['glucose'].min():.1f} - {health_data['glucose'].max():.1f} mg/dL")
    
    return health_data

def demo_federated_learning():
    """Demonstrate federated learning concepts"""
    print("\n🧠 Federated Learning Demo")
    print("=" * 40)
    
    # Simulate multiple clients
    clients = [
        {"id": 1, "name": "Patient A", "data_samples": 150, "local_accuracy": 0.89},
        {"id": 2, "name": "Patient B", "data_samples": 120, "local_accuracy": 0.92},
        {"id": 3, "name": "Patient C", "data_samples": 180, "local_accuracy": 0.87},
        {"id": 4, "name": "Patient D", "data_samples": 95, "local_accuracy": 0.91}
    ]
    
    print("Participating clients:")
    for client in clients:
        print(f"  • {client['name']}: {client['data_samples']} samples, {client['local_accuracy']:.1%} accuracy")
    
    # Simulate federated averaging
    print("\nFederated Learning Process:")
    print("1. Local training on each client's data")
    print("2. Model weights sent to central server")
    print("3. Weight aggregation (federated averaging)")
    print("4. Global model distributed back to clients")
    
    # Calculate global metrics
    total_samples = sum(client['data_samples'] for client in clients)
    avg_accuracy = np.mean([client['local_accuracy'] for client in clients])
    
    print(f"\nGlobal Model Results:")
    print(f"Total training samples: {total_samples}")
    print(f"Average local accuracy: {avg_accuracy:.1%}")
    print(f"Global model accuracy: {avg_accuracy + 0.02:.1%} (improved through aggregation)")
    
    return clients

def demo_health_predictions():
    """Demonstrate health predictions"""
    print("\n🔮 Health Predictions Demo")
    print("=" * 40)
    
    # Simulate current health status
    current_status = {
        "heart_rate": 78,
        "blood_pressure_systolic": 125,
        "glucose": 105,
        "oxygen_saturation": 97,
        "temperature": 36.9
    }
    
    print("Current Health Status:")
    for metric, value in current_status.items():
        print(f"  • {metric.replace('_', ' ').title()}: {value}")
    
    # Simulate AI predictions
    print("\nAI Predictions (next hour):")
    predictions = {
        "heart_rate": 79,
        "blood_pressure_systolic": 127,
        "glucose": 103,
        "oxygen_saturation": 97,
        "temperature": 37.0
    }
    
    for metric, value in predictions.items():
        current = current_status[metric]
        change = value - current
        change_symbol = "↗️" if change > 0 else "↘️" if change < 0 else "→"
        print(f"  • {metric.replace('_', ' ').title()}: {value} {change_symbol} {change:+d}")
    
    # Confidence scores
    confidence_scores = {
        "heart_rate": 0.89,
        "blood_pressure_systolic": 0.76,
        "glucose": 0.82,
        "oxygen_saturation": 0.94,
        "temperature": 0.91
    }
    
    print("\nPrediction Confidence:")
    for metric, confidence in confidence_scores.items():
        print(f"  • {metric.replace('_', ' ').title()}: {confidence:.1%}")
    
    return current_status, predictions, confidence_scores

def demo_alert_system():
    """Demonstrate alert system"""
    print("\n🚨 Alert System Demo")
    print("=" * 40)
    
    # Health thresholds
    thresholds = {
        "heart_rate": {"min": 60, "max": 100},
        "blood_pressure_systolic": {"min": 90, "max": 140},
        "glucose": {"min": 70, "max": 140},
        "oxygen_saturation": {"min": 95, "max": 100},
        "temperature": {"min": 36.1, "max": 37.2}
    }
    
    print("Health Thresholds:")
    for metric, limits in thresholds.items():
        print(f"  • {metric.replace('_', ' ').title()}: {limits['min']} - {limits['max']}")
    
    # Simulate alerts
    alerts = [
        {
            "type": "High Heart Rate",
            "severity": "Medium",
            "message": "Heart rate elevated: 105 bpm (Normal: 60-100)",
            "timestamp": datetime.now() - timedelta(minutes=5)
        },
        {
            "type": "Low Oxygen",
            "severity": "High",
            "message": "Oxygen saturation low: 92% (Normal: 95-100%)",
            "timestamp": datetime.now() - timedelta(minutes=2)
        },
        {
            "type": "Glucose Spike",
            "severity": "Medium",
            "message": "Glucose level high: 155 mg/dL (Normal: 70-140)",
            "timestamp": datetime.now() - timedelta(minutes=15)
        }
    ]
    
    print("\nActive Alerts:")
    for alert in alerts:
        severity_icon = {
            "Low": "🟢",
            "Medium": "🟡", 
            "High": "🟠",
            "Critical": "🔴"
        }.get(alert['severity'], "⚪")
        
        print(f"  {severity_icon} {alert['type']} ({alert['severity']})")
        print(f"    {alert['message']}")
        print(f"    Time: {alert['timestamp'].strftime('%H:%M:%S')}")
        print()
    
    return alerts

def demo_data_export():
    """Demonstrate data export capabilities"""
    print("\n📊 Data Export Demo")
    print("=" * 40)
    
    # Generate sample data
    health_data = demo_health_data_simulation()
    
    # Export to different formats
    print("Exporting health data...")
    
    # CSV export
    csv_data = health_data.to_csv(index=False)
    print(f"✅ CSV export: {len(csv_data)} characters")
    
    # JSON export
    json_data = health_data.to_json(orient='records', indent=2)
    print(f"✅ JSON export: {len(json_data)} characters")
    
    # Summary statistics
    summary = {
        "total_records": len(health_data),
        "date_range": {
            "start": health_data['timestamp'].min().isoformat(),
            "end": health_data['timestamp'].max().isoformat()
        },
        "metrics": {
            "heart_rate": {
                "mean": float(health_data['heart_rate'].mean()),
                "std": float(health_data['heart_rate'].std()),
                "min": float(health_data['heart_rate'].min()),
                "max": float(health_data['heart_rate'].max())
            },
            "glucose": {
                "mean": float(health_data['glucose'].mean()),
                "std": float(health_data['glucose'].std()),
                "min": float(health_data['glucose'].min()),
                "max": float(health_data['glucose'].max())
            }
        }
    }
    
    print(f"✅ Summary export: {len(json.dumps(summary))} characters")
    
    return health_data, summary

def main():
    """Run all demos"""
    print("🏥 Healthcare Federated Learning Application - Feature Demo")
    print("=" * 70)
    print("This demo showcases the key features without running the full application.")
    print("=" * 70)
    
    try:
        # Run all demos
        health_data = demo_health_data_simulation()
        clients = demo_federated_learning()
        current_status, predictions, confidence = demo_health_predictions()
        alerts = demo_alert_system()
        exported_data, summary = demo_data_export()
        
        print("\n" + "=" * 70)
        print("🎉 Demo completed successfully!")
        print("=" * 70)
        
        print("\nTo run the full application:")
        print("  python start.py")
        print("  # or")
        print("  streamlit run app.py")
        
        print("\nSample credentials:")
        print("  Patient: patient1 / password123")
        print("  Doctor:  doctor1 / password123")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())