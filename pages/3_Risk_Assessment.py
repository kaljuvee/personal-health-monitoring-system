import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME
import numpy as np

st.set_page_config(page_title="Risk Assessment", page_icon="⚠️", layout="wide")

st.title("⚠️ Risk Assessment")
st.markdown("Monitor patient risk scores and model performance")

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

# Sidebar controls
st.sidebar.header("Assessment Parameters")

# Time range selection
time_range = st.sidebar.selectbox(
    "Time Range",
    ["Last 24 hours", "Last 7 days", "Last 30 days", "Custom"],
    index=1
)

if time_range == "Custom":
    start_date = st.sidebar.date_input("Start Date", datetime.now().date() - timedelta(days=7))
    end_date = st.sidebar.date_input("End Date", datetime.now().date())
else:
    ranges = {
        "Last 24 hours": timedelta(days=1),
        "Last 7 days": timedelta(days=7),
        "Last 30 days": timedelta(days=30)
    }
    end_date = datetime.now().date()
    start_date = end_date - ranges[time_range]

# Risk threshold configuration
st.sidebar.subheader("Risk Thresholds")
low_risk = st.sidebar.slider("Low Risk Threshold", 0.0, 1.0, 0.3)
medium_risk = st.sidebar.slider("Medium Risk Threshold", 0.0, 1.0, 0.6)
high_risk = st.sidebar.slider("High Risk Threshold", 0.0, 1.0, 0.8)

# Fetch data from MongoDB
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
            
            # Calculate risk scores (example calculation)
            def calculate_risk_score(row):
                risk_factors = []
                
                if 'heart_rate' in row:
                    if row['heart_rate'] < 60 or row['heart_rate'] > 100:
                        risk_factors.append(0.3)
                
                if 'blood_glucose' in row:
                    if row['blood_glucose'] < 70 or row['blood_glucose'] > 180:
                        risk_factors.append(0.4)
                
                if 'spo2' in row:
                    if row['spo2'] < 95:
                        risk_factors.append(0.5)
                
                return sum(risk_factors) / len(risk_factors) if risk_factors else 0.0
            
            df['risk_score'] = df.apply(calculate_risk_score, axis=1)
            
            # Risk level categorization
            def categorize_risk(score):
                if score >= high_risk:
                    return "High"
                elif score >= medium_risk:
                    return "Medium"
                elif score >= low_risk:
                    return "Low"
                else:
                    return "Normal"
            
            df['risk_level'] = df['risk_score'].apply(categorize_risk)
            
            # Display risk distribution
            st.subheader("Risk Distribution")
            risk_dist = df['risk_level'].value_counts()
            fig = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title="Risk Level Distribution"
            )
            st.plotly_chart(fig)
            
            # Risk trends over time
            st.subheader("Risk Trends")
            daily_risk = df.groupby([df['timestamp'].dt.date, 'patient_id'])['risk_score'].mean().reset_index()
            fig = px.line(
                daily_risk,
                x='timestamp',
                y='risk_score',
                color='patient_id',
                title="Daily Risk Scores by Patient"
            )
            st.plotly_chart(fig)
            
            # Model performance metrics
            st.subheader("Model Performance Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Average Risk Score",
                    f"{df['risk_score'].mean():.2f}",
                    f"{df['risk_score'].std():.2f}"
                )
            
            with col2:
                high_risk_patients = len(df[df['risk_level'] == 'High']['patient_id'].unique())
                st.metric(
                    "High Risk Patients",
                    high_risk_patients,
                    f"{high_risk_patients / len(df['patient_id'].unique()) * 100:.1f}%"
                )
            
            with col3:
                st.metric(
                    "Risk Score Volatility",
                    f"{df.groupby('patient_id')['risk_score'].std().mean():.2f}"
                )
            
            # Patient-specific risk analysis
            st.subheader("Patient Risk Analysis")
            selected_patient = st.selectbox(
                "Select Patient",
                df['patient_id'].unique()
            )
            
            patient_data = df[df['patient_id'] == selected_patient]
            
            # Risk factors breakdown
            st.write("Risk Factors Breakdown")
            risk_factors = pd.DataFrame({
                'Factor': ['Heart Rate', 'Blood Glucose', 'SpO2'],
                'Contribution': [
                    patient_data['heart_rate'].apply(lambda x: 0.3 if x < 60 or x > 100 else 0).mean(),
                    patient_data['blood_glucose'].apply(lambda x: 0.4 if x < 70 or x > 180 else 0).mean(),
                    patient_data['spo2'].apply(lambda x: 0.5 if x < 95 else 0).mean()
                ]
            })
            
            fig = px.bar(
                risk_factors,
                x='Factor',
                y='Contribution',
                title="Risk Factor Contributions"
            )
            st.plotly_chart(fig)
            
        else:
            st.warning("No data available for the selected time range.")
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
else:
    st.error("Please check your MongoDB connection settings.") 