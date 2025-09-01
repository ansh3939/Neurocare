import streamlit as st
from auth import auth
from database import db
import streamlit as st

st.set_page_config(
    page_title="Healthcare Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Check authentication
    if not auth.is_authenticated():
        st.error("Please login to access the dashboard.")
        st.stop()
    
    user = auth.get_current_user()
    
    # Header
    st.title(f"🏥 Welcome, {user['full_name']}!")
    st.markdown(f"**Role:** {user['role'].capitalize()} | **Username:** {user['username']}")
    
    # Logout button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("🚪 Logout"):
            auth.logout_user()
            st.rerun()
    
    st.markdown("---")
    
    # Role-based dashboard routing
    if user['role'] == 'patient':
        show_patient_dashboard(user)
    elif user['role'] == 'doctor':
        show_doctor_dashboard(user)
    else:
        st.error("Unknown user role")

def show_patient_dashboard(user):
    """Show patient-specific dashboard"""
    st.header("📊 Patient Health Dashboard")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Real-time Monitoring", 
        "🧠 AI Predictions", 
        "📋 Health Records", 
        "⚙️ Settings"
    ])
    
    with tab1:
        show_real_time_monitoring(user)
    
    with tab2:
        show_ai_predictions(user)
    
    with tab3:
        show_health_records(user)
    
    with tab4:
        show_patient_settings(user)

def show_doctor_dashboard(user):
    """Show doctor-specific dashboard"""
    st.header("👨‍⚕️ Doctor Dashboard")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Patient Overview", 
        "🚨 Alerts & Monitoring", 
        "📊 Analytics", 
        "🧠 Federated Learning"
    ])
    
    with tab1:
        show_patient_overview(user)
    
    with tab2:
        show_alerts_monitoring(user)
    
    with tab3:
        show_analytics(user)
    
    with tab4:
        show_federated_learning(user)

def show_real_time_monitoring(user):
    """Show real-time health monitoring for patients"""
    st.subheader("Real-time Health Monitoring")
    
    # Add patient sensors if not already added
    from sensor_simulator import sensor_simulator
    if f"{user['id']}_heart_rate" not in sensor_simulator.sensors:
        sensor_simulator.add_patient_sensors(user['id'])
    
    # Start simulation if not running
    if not sensor_simulator.is_running:
        sensor_simulator.start_simulation()
    
    # Display current sensor values
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Heart Rate", "75 bpm", "↗️ +2")
        st.metric("Blood Pressure", "120/80", "→ 0")
    
    with col2:
        st.metric("Glucose", "100 mg/dL", "↘️ -5")
        st.metric("Oxygen", "98%", "→ 0")
    
    with col3:
        st.metric("Temperature", "36.8°C", "→ 0")
        st.metric("Status", "Normal", "✅")
    
    # Real-time charts
    st.subheader("Live Health Trends")
    
    # Simulate real-time data updates
    import time
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Create sample time series data
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Generate sample data for the last 24 hours
    timestamps = pd.date_range(
        start=datetime.now() - timedelta(hours=24),
        end=datetime.now(),
        freq='H'
    )
    
    # Simulate realistic health data
    heart_rate = np.random.normal(75, 10, len(timestamps))
    heart_rate = np.clip(heart_rate, 60, 100)
    
    blood_pressure_systolic = np.random.normal(120, 15, len(timestamps))
    blood_pressure_systolic = np.clip(blood_pressure_systolic, 90, 150)
    
    glucose = np.random.normal(100, 20, len(timestamps))
    glucose = np.clip(glucose, 70, 150)
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Heart Rate (bpm)', 'Blood Pressure (mmHg)', 'Glucose (mg/dL)'),
        vertical_spacing=0.1
    )
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=timestamps, y=heart_rate, mode='lines+markers', name='Heart Rate'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=timestamps, y=blood_pressure_systolic, mode='lines+markers', name='Systolic'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=timestamps, y=glucose, mode='lines+markers', name='Glucose'),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(height=600, showlegend=False)
    fig.update_xaxes(title_text="Time")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sensor controls
    st.subheader("Sensor Controls")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        if st.button("📊 Export Data"):
            # Generate sample CSV
            from sensor_simulator import generate_sample_csv_data
            csv_data = generate_sample_csv_data(user['id'], 24)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"health_data_{user['id']}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🚨 Test Alert"):
            st.warning("Test alert triggered! This simulates an emergency situation.")

def show_ai_predictions(user):
    """Show AI predictions and federated learning for patients"""
    st.subheader("🧠 AI Health Predictions")
    
    # Model selection
    model_type = st.selectbox("Select Model Type", ["LSTM", "GRU"], key="model_select")
    
    # Training section
    st.subheader("Train Local Model")
    
    col1, col2 = st.columns(2)
    
    with col1:
        epochs = st.slider("Training Epochs", 1, 20, 5)
        batch_size = st.slider("Batch Size", 16, 64, 32)
    
    with col2:
        if st.button("🚀 Train Model"):
            with st.spinner("Training model..."):
                # Simulate training
                import time
                time.sleep(2)
                
                # Show training progress
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                st.success("Model trained successfully!")
                
                # Show metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Loss", "0.0234", "↘️ -0.01")
                with col2:
                    st.metric("Accuracy", "94.2%", "↗️ +2.1%")
                with col3:
                    st.metric("MAE", "0.0156", "↘️ -0.008")
    
    # Predictions section
    st.subheader("Health Predictions")
    
    if st.button("🔮 Predict Next Values"):
        # Simulate prediction
        import time
        with st.spinner("Generating predictions..."):
            time.sleep(1)
        
        # Show prediction results
        st.info("Based on your recent health data, here are the predicted values for the next hour:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Predicted Heart Rate", "78 bpm", "↗️ +3")
            st.metric("Predicted BP", "122/82", "↗️ +2/+2")
        
        with col2:
            st.metric("Predicted Glucose", "98 mg/dL", "↘️ -2")
            st.metric("Predicted Oxygen", "97%", "↘️ -1")
        
        with col3:
            st.metric("Predicted Temp", "36.9°C", "↗️ +0.1")
            st.metric("Confidence", "87%", "✅")
    
    # Federated Learning section
    st.subheader("🌐 Federated Learning")
    
    st.info("""
    **Federated Learning Status:** Your local model contributes to a global healthcare model 
    without sharing your personal data. The global model learns from patterns across all 
    patients while maintaining privacy.
    """)
    
    if st.button("🔄 Participate in FL Round"):
        with st.spinner("Participating in federated learning round..."):
            time.sleep(2)
        
        st.success("Successfully participated in federated learning round!")
        st.info("Your model weights have been aggregated with other patients' models.")
        
        # Show FL metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Global Model Accuracy", "91.3%", "↗️ +1.2%")
            st.metric("Participants", "47", "↗️ +3")
        with col2:
            st.metric("Your Contribution", "High", "✅")
            st.metric("Privacy Level", "100%", "🔒")

def show_health_records(user):
    """Show patient health records and history"""
    st.subheader("📋 Health Records")
    
    # Time range selection
    col1, col2 = st.columns(2)
    with col1:
        hours = st.selectbox("Time Range", [6, 12, 24, 48, 72], index=2)
    with col2:
        if st.button("🔄 Refresh Records"):
            st.rerun()
    
    # Get health records from database
    records = db.get_patient_health_records(user['id'], hours)
    
    if records.empty:
        st.info("No health records found for the selected time range.")
        
        # Generate sample data
        if st.button("📊 Generate Sample Data"):
            from ml_models import simulate_health_data
            sample_data = simulate_health_data(hours)
            
            # Save to database
            for _, row in sample_data.iterrows():
                health_data = {
                    'heart_rate': int(row['heart_rate']),
                    'blood_pressure_systolic': int(row['blood_pressure_systolic']),
                    'blood_pressure_diastolic': int(row['blood_pressure_diastolic']),
                    'glucose': float(row['glucose']),
                    'oxygen_saturation': float(row['oxygen_saturation']),
                    'temperature': float(row['temperature'])
                }
                db.add_health_record(user['id'], health_data)
            
            st.success("Sample data generated and saved!")
            st.rerun()
    else:
        # Display records
        st.dataframe(records, use_container_width=True)
        
        # Download option
        csv_data = records.to_csv(index=False)
        st.download_button(
            label="📥 Download Records",
            data=csv_data,
            file_name=f"health_records_{user['id']}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_patient_settings(user):
    """Show patient settings and preferences"""
    st.subheader("⚙️ Settings & Preferences")
    
    # Profile information
    st.write("**Profile Information**")
    st.write(f"**Name:** {user['full_name']}")
    st.write(f"**Email:** {user['email']}")
    st.write(f"**User ID:** {user['id']}")
    
    # Alert preferences
    st.subheader("Alert Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_alerts = st.checkbox("Email Alerts", value=True)
        push_notifications = st.checkbox("Push Notifications", value=True)
    
    with col2:
        critical_alerts = st.checkbox("Critical Alerts Only", value=False)
        daily_summary = st.checkbox("Daily Health Summary", value=True)
    
    if st.button("💾 Save Preferences"):
        st.success("Preferences saved successfully!")
    
    # Data privacy
    st.subheader("Data Privacy")
    
    st.info("""
    🔒 **Your data is protected:**
    - All health data is encrypted and stored locally
    - Federated learning only shares model weights, never raw data
    - You control what data is shared and with whom
    """)
    
    if st.button("📊 Export All My Data"):
        st.info("This will export all your health data in a secure format.")
        # Implementation for data export

def show_patient_overview(user):
    """Show overview of all patients for doctors"""
    st.subheader("👥 Patient Overview")
    
    # Get all patients
    patients = db.get_all_patients()
    
    if not patients:
        st.info("No patients registered yet.")
        return
    
    # Display patients in a table
    st.dataframe(patients, use_container_width=True)
    
    # Patient selection for detailed view
    if patients:
        selected_patient = st.selectbox(
            "Select Patient for Detailed View",
            options=[f"{p['full_name']} ({p['username']})" for p in patients],
            key="patient_select"
        )
        
        if selected_patient:
            # Get selected patient ID
            patient_username = selected_patient.split("(")[1].split(")")[0]
            selected_patient_data = next(p for p in patients if p['username'] == patient_username)
            
            st.subheader(f"Patient Details: {selected_patient_data['full_name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Username:** {selected_patient_data['username']}")
                st.write(f"**Email:** {selected_patient_data['email']}")
                st.write(f"**Age:** {selected_patient_data['age'] or 'Not specified'}")
                st.write(f"**Gender:** {selected_patient_data['gender'] or 'Not specified'}")
            
            with col2:
                # Quick health status
                st.write("**Quick Health Status**")
                st.metric("Last Update", "2 hours ago")
                st.metric("Status", "Normal", "✅")
                st.metric("Risk Level", "Low", "🟢")
            
            # View patient records button
            if st.button(f"📋 View {selected_patient_data['full_name']}'s Records"):
                st.session_state['selected_patient_id'] = selected_patient_data['id']
                st.rerun()

def show_alerts_monitoring(user):
    """Show alerts and monitoring for doctors"""
    st.subheader("🚨 Alerts & Monitoring")
    
    # Alert filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alert_severity = st.selectbox("Severity", ["All", "Low", "Medium", "High", "Critical"])
    with col2:
        alert_type = st.selectbox("Type", ["All", "Health Threshold", "Anomaly", "System"])
    with col3:
        if st.button("🔄 Refresh Alerts"):
            st.rerun()
    
    # Simulate alerts
    sample_alerts = [
        {
            "patient": "John Doe",
            "type": "Health Threshold",
            "message": "Heart rate above normal: 105 bpm",
            "severity": "High",
            "time": "2 minutes ago"
        },
        {
            "patient": "Jane Smith",
            "type": "Anomaly",
            "message": "Unusual glucose pattern detected",
            "severity": "Medium",
            "time": "15 minutes ago"
        },
        {
            "patient": "Mike Johnson",
            "type": "System",
            "message": "Sensor connection lost",
            "severity": "Low",
            "time": "1 hour ago"
        }
    ]
    
    # Filter alerts
    if alert_severity != "All":
        sample_alerts = [a for a in sample_alerts if a['severity'].lower() == alert_severity.lower()]
    
    if alert_type != "All":
        sample_alerts = [a for a in sample_alerts if a['type'] == alert_type]
    
    # Display alerts
    for alert in sample_alerts:
        severity_color = {
            "Low": "🟢",
            "Medium": "🟡",
            "High": "🟠",
            "Critical": "🔴"
        }.get(alert['severity'], "⚪")
        
        with st.expander(f"{severity_color} {alert['patient']} - {alert['type']}"):
            st.write(f"**Message:** {alert['message']}")
            st.write(f"**Severity:** {alert['severity']}")
            st.write(f"**Time:** {alert['time']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Mark as Read", key=f"read_{alert['patient']}"):
                    st.success("Alert marked as read!")
            with col2:
                if st.button("📞 Contact Patient", key=f"contact_{alert['patient']}"):
                    st.info("Contacting patient...")

def show_analytics(user):
    """Show analytics and insights for doctors"""
    st.subheader("📊 Analytics & Insights")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", "47", "↗️ +3")
    with col2:
        st.metric("Active Alerts", "5", "↘️ -2")
    with col3:
        st.metric("Avg Health Score", "87.3", "↗️ +1.2")
    with col4:
        st.metric("Risk Patients", "3", "→ 0")
    
    # Charts
    st.subheader("Patient Health Trends")
    
    import plotly.graph_objects as go
    import numpy as np
    
    # Sample data for charts
    days = list(range(1, 31))
    avg_heart_rate = np.random.normal(75, 5, 30)
    avg_glucose = np.random.normal(100, 15, 30)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=days, y=avg_heart_rate,
        mode='lines+markers',
        name='Average Heart Rate',
        line=dict(color='red', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=days, y=avg_glucose,
        mode='lines+markers',
        name='Average Glucose',
        line=dict(color='blue', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="30-Day Health Trends",
        xaxis_title="Day",
        yaxis=dict(title="Heart Rate (bpm)", side='left'),
        yaxis2=dict(title="Glucose (mg/dL)", side='right', overlaying='y'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk analysis
    st.subheader("Risk Analysis")
    
    risk_data = {
        "Patient": ["John Doe", "Jane Smith", "Mike Johnson"],
        "Risk Factor": ["High BP", "Diabetes", "Age"],
        "Risk Level": ["Medium", "High", "Low"],
        "Last Check": ["2 days ago", "1 day ago", "3 days ago"]
    }
    
    st.dataframe(risk_data, use_container_width=True)

def show_federated_learning(user):
    """Show federated learning status and management for doctors"""
    st.subheader("🧠 Federated Learning Management")
    
    st.info("""
    **Federated Learning Status:** The system is actively learning from patient data 
    across all devices while maintaining complete privacy. No raw data is ever shared 
    between patients or with the central server.
    """)
    
    # FL Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Clients", "47", "↗️ +2")
        st.metric("Training Rounds", "23", "↗️ +1")
    
    with col2:
        st.metric("Global Accuracy", "91.3%", "↗️ +1.2%")
        st.metric("Avg Loss", "0.0234", "↘️ -0.008")
    
    with col3:
        st.metric("Privacy Level", "100%", "🔒")
        st.metric("Data Security", "AES-256", "🔐")
    
    # FL Controls
    st.subheader("Federated Learning Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start FL Round"):
            with st.spinner("Starting federated learning round..."):
                import time
                time.sleep(2)
            
            st.success("Federated learning round started!")
            st.info("All participating clients are now training their local models.")
        
        if st.button("⏸️ Pause FL"):
            st.warning("Federated learning paused.")
    
    with col2:
        if st.button("📊 View FL Progress"):
            st.info("Loading federated learning progress...")
            # Implementation for FL progress visualization
        
        if st.button("🔄 Reset Global Model"):
            if st.checkbox("I understand this will reset the global model"):
                st.warning("Global model reset. All clients will need to retrain.")
    
    # FL Progress Chart
    st.subheader("Training Progress")
    
    import plotly.graph_objects as go
    
    # Sample FL progress data
    rounds = list(range(1, 24))
    accuracy = [85 + i * 0.3 + np.random.normal(0, 0.5) for i in rounds]
    loss = [0.1 - i * 0.003 + np.random.normal(0, 0.01) for i in rounds]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rounds, y=accuracy,
        mode='lines+markers',
        name='Global Accuracy',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=rounds, y=[l * 100 for l in loss],  # Scale loss for visualization
        mode='lines+markers',
        name='Global Loss (scaled)',
        line=dict(color='red', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Federated Learning Progress",
        xaxis_title="Training Round",
        yaxis=dict(title="Accuracy (%)", side='left'),
        yaxis2=dict(title="Loss (scaled)", side='right', overlaying='y'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()