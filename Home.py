import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Personal Health Monitoring System",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Personal Health Monitoring System (PHMS)")
st.subheader("AI-Powered Health Companion Agent")

# Introduction
st.markdown("""
### Welcome to the Personal Health Monitoring System

This system provides real-time health monitoring and personalized interventions using advanced AI technology. 
The system integrates data from various sources to provide comprehensive health insights and timely alerts.

#### Key Features:
- 📊 Real-time health data monitoring
- 🤖 AI-powered risk assessment
- 🔔 Personalized health alerts
- 📱 Behavioral intervention recommendations
- 👨‍⚕️ Care provider escalation when needed
- 📈 Continuous learning and personalization

#### Data Sources:
- Wearable devices (heart rate, glucose, SpO2, sleep)
- Electronic Health Records (EHR)
- Behavioral logs (diet, activity, mood)
""")

# System Status
st.markdown("### System Status")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Active Users", value="1,234")
with col2:
    st.metric(label="Alerts Today", value="45")
with col3:
    st.metric(label="System Uptime", value="99.9%")

# Quick Navigation
st.markdown("### Quick Navigation")
st.markdown("""
- [Data Generation](/pages/1_Data_Generation.py) - Generate synthetic health data
- [Data Ingestion](/pages/2_Data_Ingestion.py) - Ingest and process health data
- [Risk Assessment](/pages/3_Risk_Assessment.py) - AI-powered risk analysis
- [Alert Management](/pages/4_Alert_Management.py) - Configure and manage alerts
- [User Settings](/pages/5_User_Settings.py) - Personalize monitoring parameters
- [Analytics Dashboard](/pages/6_Analytics_Dashboard.py) - View insights and trends
""")

# Recent Activity
st.markdown("### Recent Activity")
activity_data = pd.DataFrame({
    'Time': [datetime.now() - timedelta(minutes=x) for x in range(5)],
    'Event': ['Alert Generated', 'Data Sync', 'Risk Assessment', 'User Login', 'System Update'],
    'Status': ['Completed', 'Completed', 'In Progress', 'Completed', 'Completed']
})
st.dataframe(activity_data, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ for better healthcare</p>
    <p>Version 1.0.0 | Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True)

# Add a new section for the PyTorch model description
st.markdown("""
## PyTorch Model for Risk Assessment

The health agent utilizes a PyTorch-based LSTM (Long Short-Term Memory) model for real-time risk assessment. This model is designed to analyze sequential health data and predict potential health risks based on historical and current metrics.

### Model Architecture

- **Input Layer**: The model takes a sequence of health metrics (e.g., heart rate, blood glucose, SpO2) as input.
- **LSTM Layer**: A bidirectional LSTM layer processes the input sequence, capturing temporal dependencies and patterns in the data.
- **Fully Connected Layers**: The output from the LSTM is passed through fully connected layers to produce a risk score.
- **Output Layer**: The final layer uses a sigmoid activation function to output a risk score between 0 and 1, where higher scores indicate greater health risks.

### Functionality

- **Risk Assessment**: The model assesses the risk of health anomalies by analyzing trends and patterns in the input data.
- **Real-Time Monitoring**: It continuously processes incoming health data to provide real-time risk assessments and alerts.
- **Integration with Health Agent**: The model is integrated into the health agent to enhance its ability to detect and respond to potential health issues promptly.

This model is a critical component of the health monitoring system, enabling proactive health management and timely interventions.
""")
