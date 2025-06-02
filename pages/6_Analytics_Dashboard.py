import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from agent.health_agent import create_health_agent, HealthData, AgentState

st.set_page_config(page_title="Analytics Dashboard", page_icon="📈", layout="wide")

st.title("📈 Health Analytics Dashboard")
st.markdown("Monitor health metrics and agent responses in real-time")

# Load data
@st.cache_data
def load_health_data():
    """Load health data from JSON file and convert to DataFrame."""
    if os.path.exists('data/synthetic_health_data.json'):
        with open('data/synthetic_health_data.json', 'r') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Convert timestamp strings to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract vitals into separate columns
        if 'vitals' in df.columns:
            df['systolic'] = df['vitals'].apply(lambda x: x.get('systolic') if x else None)
            df['diastolic'] = df['vitals'].apply(lambda x: x.get('diastolic') if x else None)
            df = df.drop('vitals', axis=1)
        
        return df
    return None

# Initialize session state for agent
if 'health_agent' not in st.session_state:
    st.session_state['health_agent'] = create_health_agent()

# Load data
df = load_health_data()

if df is not None:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Patient selection
    selected_patient = st.sidebar.selectbox(
        "Select Patient",
        df['patient_id'].unique()
    )
    
    # Date range selection
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        min_value=df['timestamp'].min().date(),
        max_value=df['timestamp'].max().date()
    )
    
    # Filter data
    filtered_df = df[
        (df['patient_id'] == selected_patient) &
        (df['timestamp'].dt.date >= date_range[0]) &
        (df['timestamp'].dt.date <= date_range[1])
    ]
    
    # Main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Health Metrics")
        
        # Create tabs for different metrics
        metric_tabs = st.tabs(["Vital Signs", "Activity & Sleep", "Risk Analysis", "Raw Data"])
        
        with metric_tabs[0]:
            # Vital signs plot
            vital_signs = ['heart_rate', 'systolic', 'diastolic', 'blood_glucose', 'spo2']
            vital_data = filtered_df[vital_signs].copy()
            vital_data['timestamp'] = filtered_df['timestamp']
            
            fig_vitals = go.Figure()
            for col in vital_signs:
                if col in vital_data.columns and not vital_data[col].isna().all():
                    fig_vitals.add_trace(
                        go.Scatter(
                            x=vital_data['timestamp'],
                            y=vital_data[col],
                            name=col.replace('_', ' ').title(),
                            mode='lines+markers'
                        )
                    )
            
            fig_vitals.update_layout(
                title="Vital Signs Over Time",
                xaxis_title="Time",
                yaxis_title="Value",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_vitals, use_container_width=True)
        
        with metric_tabs[1]:
            # Activity and sleep plot
            activity_data = filtered_df[['activity', 'sleep']].copy()
            activity_data['timestamp'] = filtered_df['timestamp']
            
            fig_activity = go.Figure()
            for col in ['activity', 'sleep']:
                if col in activity_data.columns and not activity_data[col].isna().all():
                    fig_activity.add_trace(
                        go.Scatter(
                            x=activity_data['timestamp'],
                            y=activity_data[col],
                            name=col.replace('_', ' ').title(),
                            mode='lines+markers'
                        )
                    )
            
            fig_activity.update_layout(
                title="Activity and Sleep Patterns",
                xaxis_title="Time",
                yaxis_title="Value",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_activity, use_container_width=True)
        
        with metric_tabs[2]:
            # Risk analysis
            st.subheader("Risk Analysis")
            
            # Process data through health agent
            risk_scores = []
            alerts = []
            
            for _, row in filtered_df.iterrows():
                health_data = HealthData(
                    patient_id=row['patient_id'],
                    timestamp=row['timestamp'],
                    heart_rate=row.get('heart_rate'),
                    systolic=row.get('systolic'),
                    diastolic=row.get('diastolic'),
                    blood_glucose=row.get('blood_glucose'),
                    spo2=row.get('spo2'),
                    sleep=row.get('sleep'),
                    activity=row.get('activity'),
                    mood=row.get('mood')
                )
                
                state = AgentState(
                    current_data=health_data,
                    historical_data=[],
                    alerts=[],
                    risk_score=0.0
                )
                
                result = st.session_state['health_agent'].invoke(state)
                risk_scores.append(result.risk_score)
                alerts.append(result.alerts[-1] if result.alerts else None)
            
            # Plot risk scores
            fig_risk = go.Figure()
            fig_risk.add_trace(
                go.Scatter(
                    x=filtered_df['timestamp'],
                    y=risk_scores,
                    name="Risk Score",
                    mode='lines+markers'
                )
            )
            
            fig_risk.update_layout(
                title="Risk Score Over Time",
                xaxis_title="Time",
                yaxis_title="Risk Score",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_risk, use_container_width=True)
            
            # Add mood analysis
            if 'mood' in filtered_df.columns:
                mood_counts = filtered_df['mood'].value_counts()
                fig_mood = px.pie(
                    values=mood_counts.values,
                    names=mood_counts.index,
                    title="Mood Distribution"
                )
                st.plotly_chart(fig_mood, use_container_width=True)
        
        with metric_tabs[3]:
            # Raw data view
            st.subheader("Raw Data")
            st.dataframe(
                filtered_df.drop(['metadata'], axis=1, errors='ignore'),
                use_container_width=True
            )
    
    with col2:
        st.subheader("Latest Alerts")
        
        # Display latest alerts
        if alerts:
            latest_alert = alerts[-1]
            alert_color = {
                "severe": "red",
                "mild": "orange",
                "none": "green"
            }.get(latest_alert.level, "gray")
            
            st.markdown(f"""
            <div style='padding: 20px; border-radius: 10px; background-color: {alert_color}20; border: 1px solid {alert_color}'>
                <h3 style='color: {alert_color}'>{latest_alert.level.title()} Alert</h3>
                <p>{latest_alert.message}</p>
                <p><strong>Action Required:</strong> {'Yes' if latest_alert.action_required else 'No'}</p>
                <p><strong>Escalation Needed:</strong> {'Yes' if latest_alert.escalation_needed else 'No'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("Summary Statistics")
        
        # Calculate summary statistics
        if 'heart_rate' in filtered_df.columns:
            st.metric(
                "Average Heart Rate",
                f"{filtered_df['heart_rate'].mean():.1f} bpm",
                delta=f"{filtered_df['heart_rate'].iloc[-1] - filtered_df['heart_rate'].iloc[-2]:.1f}" if len(filtered_df) > 1 else None
            )
        
        if 'blood_glucose' in filtered_df.columns:
            st.metric(
                "Average Blood Glucose",
                f"{filtered_df['blood_glucose'].mean():.1f} mg/dL",
                delta=f"{filtered_df['blood_glucose'].iloc[-1] - filtered_df['blood_glucose'].iloc[-2]:.1f}" if len(filtered_df) > 1 else None
            )
        
        if 'activity' in filtered_df.columns:
            st.metric(
                "Average Daily Activity",
                f"{filtered_df['activity'].mean():.0f} steps",
                delta=f"{filtered_df['activity'].iloc[-1] - filtered_df['activity'].iloc[-2]:.0f}" if len(filtered_df) > 1 else None
            )
        
        # Risk score summary
        if risk_scores:
            st.metric(
                "Current Risk Score",
                f"{risk_scores[-1]:.2f}",
                delta=f"{risk_scores[-1] - risk_scores[-2]:.2f}" if len(risk_scores) > 1 else None
            )
        
        # Add correlation matrix
        st.subheader("Metric Correlations")
        numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 1:
            corr_matrix = filtered_df[numeric_cols].corr()
            fig_corr = px.imshow(
                corr_matrix,
                title="Correlation Matrix",
                color_continuous_scale='RdBu'
            )
            st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.warning("No health data available. Please generate data first.") 