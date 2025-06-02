import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from agent.health_agent import create_health_agent, HealthData, AgentState

st.set_page_config(page_title="Data Generation", page_icon="📊", layout="wide")

st.title("📊 Health Data Generation")
st.markdown("Generate synthetic health data for testing and development")

# Initialize session state for agent
if 'health_agent' not in st.session_state:
    st.session_state['health_agent'] = create_health_agent()

# Sidebar controls
st.sidebar.header("Generation Parameters")

# Time range selection
start_date = st.sidebar.date_input(
    "Start Date",
    value=datetime.now().date() - timedelta(days=7)
)
end_date = st.sidebar.date_input(
    "End Date",
    value=datetime.now().date()
)

# Data collection frequency
frequency = st.sidebar.selectbox(
    "Data Collection Frequency",
    ["1 minute", "5 minutes", "15 minutes", "30 minutes", "1 hour"],
    index=2
)

# Number of patients
num_patients = st.sidebar.number_input(
    "Number of Patients",
    min_value=1,
    max_value=10,
    value=5
)

# Health metrics selection
st.sidebar.subheader("Health Metrics")
metrics = {
    "heart_rate": st.sidebar.checkbox("Heart Rate", value=True),
    "blood_pressure": st.sidebar.checkbox("Blood Pressure", value=True),
    "blood_glucose": st.sidebar.checkbox("Blood Glucose", value=True),
    "spo2": st.sidebar.checkbox("SpO2", value=True),
    "sleep": st.sidebar.checkbox("Sleep", value=True),
    "activity": st.sidebar.checkbox("Activity", value=True),
    "mood": st.sidebar.checkbox("Mood", value=True)
}

# Threshold settings
st.sidebar.subheader("Alert Thresholds")
thresholds = {
    "heart_rate": {
        "low": st.sidebar.number_input("Heart Rate Low", value=60),
        "high": st.sidebar.number_input("Heart Rate High", value=100)
    },
    "blood_glucose": {
        "low": st.sidebar.number_input("Blood Glucose Low", value=70),
        "high": st.sidebar.number_input("Blood Glucose High", value=180)
    },
    "spo2": {
        "low": st.sidebar.number_input("SpO2 Low", value=95),
        "high": st.sidebar.number_input("SpO2 High", value=100)
    }
}

def generate_synthetic_data():
    """Generate synthetic health data based on selected parameters."""
    # Convert frequency to minutes
    freq_map = {
        "1 minute": 1,
        "5 minutes": 5,
        "15 minutes": 15,
        "30 minutes": 30,
        "1 hour": 60
    }
    freq_minutes = freq_map[frequency]
    
    # Generate timestamps
    timestamps = pd.date_range(
        start=datetime.combine(start_date, datetime.min.time()),
        end=datetime.combine(end_date, datetime.max.time()),
        freq=f"{freq_minutes}T"
    )
    
    data = []
    for patient_id in range(1, num_patients + 1):
        patient_id = f"P{patient_id:03d}"
        
        # Generate baseline values with some randomness
        baseline = {
            "heart_rate": np.random.normal(75, 5),
            "systolic": np.random.normal(120, 5),
            "diastolic": np.random.normal(80, 5),
            "blood_glucose": np.random.normal(100, 10),
            "spo2": np.random.normal(98, 0.5),
            "sleep": np.random.normal(7, 1),
            "activity": np.random.normal(5000, 1000)
        }
        
        for timestamp in timestamps:
            record = {
                "patient_id": patient_id,
                "timestamp": timestamp.isoformat(),
                "metadata": {
                    "source": "synthetic",
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            # Add selected metrics with realistic variations
            if metrics["heart_rate"]:
                record["heart_rate"] = max(40, min(200, np.random.normal(baseline["heart_rate"], 5)))
            
            if metrics["blood_pressure"]:
                record["systolic"] = max(80, min(200, np.random.normal(baseline["systolic"], 5)))
                record["diastolic"] = max(50, min(120, np.random.normal(baseline["diastolic"], 5)))
            
            if metrics["blood_glucose"]:
                record["blood_glucose"] = max(50, min(300, np.random.normal(baseline["blood_glucose"], 10)))
            
            if metrics["spo2"]:
                record["spo2"] = max(90, min(100, np.random.normal(baseline["spo2"], 0.5)))
            
            if metrics["sleep"]:
                record["sleep"] = max(0, min(12, np.random.normal(baseline["sleep"], 1)))
            
            if metrics["activity"]:
                record["activity"] = max(0, min(20000, np.random.normal(baseline["activity"], 1000)))
            
            if metrics["mood"]:
                record["mood"] = np.random.choice(["happy", "neutral", "stressed", "tired"])
            
            data.append(record)
    
    return data

def process_data_with_agent(data):
    """Process generated data through the health agent."""
    alerts = []
    for record in data:
        health_data = HealthData(
            patient_id=record["patient_id"],
            timestamp=datetime.fromisoformat(record["timestamp"]),
            heart_rate=record.get("heart_rate"),
            systolic=record.get("systolic"),
            diastolic=record.get("diastolic"),
            blood_glucose=record.get("blood_glucose"),
            spo2=record.get("spo2"),
            sleep=record.get("sleep"),
            activity=record.get("activity"),
            mood=record.get("mood"),
            metadata=record.get("metadata")
        )
        
        state = AgentState(
            current_data=health_data,
            historical_data=[],
            alerts=[],
            risk_score=0.0
        )
        
        result = st.session_state['health_agent'].invoke(state)
        if result.alerts:
            alerts.append({
                "patient_id": record["patient_id"],
                "timestamp": record["timestamp"],
                "alert": result.alerts[-1]
            })
    
    return alerts

# Generate data button
if st.sidebar.button("Generate Data"):
    with st.spinner("Generating synthetic health data..."):
        # Generate data
        data = generate_synthetic_data()
        
        # Save to JSON file
        os.makedirs("data", exist_ok=True)
        with open("data/synthetic_health_data.json", "w") as f:
            json.dump(data, f, indent=2)
        
        # Process through health agent
        alerts = process_data_with_agent(data)
        
        # Display results
        st.success(f"Generated {len(data)} records for {num_patients} patients")
        
        # Show sample data
        st.subheader("Sample Data")
        st.json(data[0])
        
        # Show alerts
        if alerts:
            st.subheader("Generated Alerts")
            for alert in alerts[:5]:  # Show first 5 alerts
                st.markdown(f"""
                **Patient {alert['patient_id']}** at {alert['timestamp']}
                - Level: {alert['alert'].level}
                - Message: {alert['alert'].message}
                - Action Required: {alert['alert'].action_required}
                - Escalation Needed: {alert['alert'].escalation_needed}
                """)
        
        # Show data preview
        st.subheader("Data Preview")
        df = pd.DataFrame(data)
        st.dataframe(df.head())
        
        # Show data statistics
        st.subheader("Data Statistics")
        if "heart_rate" in df.columns:
            st.metric("Average Heart Rate", f"{df['heart_rate'].mean():.1f} bpm")
        if "blood_glucose" in df.columns:
            st.metric("Average Blood Glucose", f"{df['blood_glucose'].mean():.1f} mg/dL")
        if "activity" in df.columns:
            st.metric("Average Activity", f"{df['activity'].mean():.0f} steps")

# Add data visualization
if os.path.exists("data/synthetic_health_data.json"):
    st.subheader("Data Visualization")
    
    # Load data
    with open("data/synthetic_health_data.json", "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Patient selection
    selected_patient = st.selectbox(
        "Select Patient",
        df['patient_id'].unique()
    )
    
    # Filter data
    filtered_df = df[df['patient_id'] == selected_patient]
    
    # Plot metrics
    if "heart_rate" in filtered_df.columns:
        st.line_chart(filtered_df.set_index('timestamp')['heart_rate'])
    
    if "blood_glucose" in filtered_df.columns:
        st.line_chart(filtered_df.set_index('timestamp')['blood_glucose'])
    
    if "activity" in filtered_df.columns:
        st.line_chart(filtered_df.set_index('timestamp')['activity']) 