import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

st.set_page_config(page_title="Alert Management", page_icon="🔔", layout="wide")

st.title("🔔 Alert Management")
st.markdown("Configure and monitor health alerts")

# Initialize MongoDB connection
@st.cache_resource
def get_mongodb_connection():
    try:
        client = MongoClient(MONGODB_URI)
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {str(e)}")
        return None

# Alert Rules Configuration
st.sidebar.header("Alert Rules")

# Metric selection
metric = st.sidebar.selectbox(
    "Health Metric",
    ["Heart Rate", "Blood Glucose", "SpO2", "Blood Pressure"]
)

# Threshold configuration
st.sidebar.subheader("Thresholds")
if metric == "Blood Pressure":
    systolic_low = st.sidebar.number_input("Systolic Low", value=90)
    systolic_high = st.sidebar.number_input("Systolic High", value=140)
    diastolic_low = st.sidebar.number_input("Diastolic Low", value=60)
    diastolic_high = st.sidebar.number_input("Diastolic High", value=90)
else:
    low_threshold = st.sidebar.number_input("Low Threshold", value=60 if metric == "Heart Rate" else 70 if metric == "Blood Glucose" else 95)
    high_threshold = st.sidebar.number_input("High Threshold", value=100 if metric == "Heart Rate" else 180 if metric == "Blood Glucose" else 100)

# Alert severity
severity = st.sidebar.selectbox(
    "Alert Severity",
    ["Low", "Medium", "High", "Critical"]
)

# Escalation path
st.sidebar.subheader("Escalation Path")
escalation_steps = st.sidebar.multiselect(
    "Escalation Steps",
    ["Notify Patient", "Notify Care Provider", "Notify Emergency Services", "Schedule Follow-up"],
    default=["Notify Patient", "Notify Care Provider"]
)

# Save rule button
if st.sidebar.button("Save Alert Rule"):
    st.sidebar.success("Alert rule saved successfully!")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Alert History")
    
    # Time range selection
    time_range = st.selectbox(
        "Time Range",
        ["Last 24 hours", "Last 7 days", "Last 30 days", "Custom"],
        index=1
    )
    
    if time_range == "Custom":
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
        end_date = st.date_input("End Date", datetime.now().date())
    else:
        ranges = {
            "Last 24 hours": timedelta(days=1),
            "Last 7 days": timedelta(days=7),
            "Last 30 days": timedelta(days=30)
        }
        end_date = datetime.now().date()
        start_date = end_date - ranges[time_range]
    
    # Fetch alerts from MongoDB
    client = get_mongodb_connection()
    if client:
        try:
            db = client[MONGODB_DB_NAME]
            collection = db[MONGODB_COLLECTION_NAME]
            
            # Query data within time range
            query = {
                "timestamp": {
                    "$gte": datetime.combine(start_date, datetime.min.time()).isoformat(),
                    "$lte": datetime.combine(end_date, datetime.max.time()).isoformat()
                }
            }
            
            data = list(collection.find(query))
            
            if data:
                # Convert to DataFrame
                df = pd.DataFrame(data)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Generate sample alerts (in a real system, these would come from the database)
                alerts = []
                for _, row in df.iterrows():
                    if metric == "Heart Rate" and 'heart_rate' in row:
                        if row['heart_rate'] < low_threshold or row['heart_rate'] > high_threshold:
                            alerts.append({
                                'timestamp': row['timestamp'],
                                'patient_id': row['patient_id'],
                                'metric': 'Heart Rate',
                                'value': row['heart_rate'],
                                'severity': severity,
                                'message': f"Heart rate {row['heart_rate']} outside normal range"
                            })
                    elif metric == "Blood Glucose" and 'blood_glucose' in row:
                        if row['blood_glucose'] < low_threshold or row['blood_glucose'] > high_threshold:
                            alerts.append({
                                'timestamp': row['timestamp'],
                                'patient_id': row['patient_id'],
                                'metric': 'Blood Glucose',
                                'value': row['blood_glucose'],
                                'severity': severity,
                                'message': f"Blood glucose {row['blood_glucose']} outside normal range"
                            })
                    elif metric == "SpO2" and 'spo2' in row:
                        if row['spo2'] < low_threshold:
                            alerts.append({
                                'timestamp': row['timestamp'],
                                'patient_id': row['patient_id'],
                                'metric': 'SpO2',
                                'value': row['spo2'],
                                'severity': severity,
                                'message': f"SpO2 {row['spo2']} below threshold"
                            })
                
                if alerts:
                    alerts_df = pd.DataFrame(alerts)
                    
                    # Display alerts table
                    st.dataframe(alerts_df)
                    
                    # Alert trends
                    st.subheader("Alert Trends")
                    daily_alerts = alerts_df.groupby([alerts_df['timestamp'].dt.date, 'severity']).size().reset_index(name='count')
                    fig = px.line(
                        daily_alerts,
                        x='timestamp',
                        y='count',
                        color='severity',
                        title="Daily Alerts by Severity"
                    )
                    st.plotly_chart(fig)
                else:
                    st.info("No alerts generated for the selected criteria.")
            else:
                st.warning("No data available for the selected time range.")
                
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
        finally:
            client.close()
    else:
        st.error("Please check your MongoDB connection settings.")

with col2:
    st.subheader("Active Alerts")
    
    # Sample active alerts (in a real system, these would come from the database)
    active_alerts = [
        {
            "patient_id": "P001",
            "metric": "Heart Rate",
            "value": 110,
            "severity": "High",
            "timestamp": datetime.now() - timedelta(minutes=5)
        },
        {
            "patient_id": "P002",
            "metric": "Blood Glucose",
            "value": 190,
            "severity": "Medium",
            "timestamp": datetime.now() - timedelta(minutes=15)
        }
    ]
    
    for alert in active_alerts:
        with st.container():
            st.markdown(f"""
            ### {alert['patient_id']}
            **{alert['metric']}**: {alert['value']}
            - Severity: {alert['severity']}
            - Time: {alert['timestamp'].strftime('%H:%M:%S')}
            """)
            if st.button("Acknowledge", key=alert['patient_id']):
                st.success(f"Alert for {alert['patient_id']} acknowledged")
    
    st.subheader("Escalation Status")
    escalation_status = {
        "Notify Patient": "Completed",
        "Notify Care Provider": "In Progress",
        "Notify Emergency Services": "Not Started",
        "Schedule Follow-up": "Not Started"
    }
    
    for step, status in escalation_status.items():
        st.markdown(f"- {step}: {status}") 