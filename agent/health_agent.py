from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass
import mlflow
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Define data models
@dataclass
class HealthData:
    patient_id: str
    timestamp: datetime
    heart_rate: Optional[float] = None
    systolic: Optional[float] = None
    diastolic: Optional[float] = None
    blood_glucose: Optional[float] = None
    spo2: Optional[float] = None
    sleep: Optional[float] = None
    activity: Optional[float] = None
    mood: Optional[str] = None
    metadata: Optional[Dict] = None

@dataclass
class Alert:
    level: str  # "severe", "mild", "none"
    message: str
    action_required: bool
    escalation_needed: bool
    explanation: str
    timestamp: datetime
    confidence: float

@dataclass
class AgentState:
    current_data: HealthData
    historical_data: List[HealthData]
    alerts: List[Alert]
    risk_score: float
    patient_thresholds: Dict[str, Dict[str, float]] = None
    model_version: str = None

class HealthDataset(Dataset):
    def __init__(self, data: List[HealthData], sequence_length: int = 10):
        self.data = data
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        self._prepare_data()
    
    def _prepare_data(self):
        # Convert data to numpy arrays
        features = []
        for d in self.data:
            features.append([
                d.heart_rate or 0,
                d.systolic or 0,
                d.diastolic or 0,
                d.blood_glucose or 0,
                d.spo2 or 0,
                d.sleep or 0,
                d.activity or 0
            ])
        self.features = self.scaler.fit_transform(features)
    
    def __len__(self):
        return len(self.data) - self.sequence_length
    
    def __getitem__(self, idx):
        sequence = self.features[idx:idx + self.sequence_length]
        return torch.FloatTensor(sequence)

class RiskAssessmentModel(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            batch_first=True
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])

class HealthAgent:
    def __init__(self):
        self.model = RiskAssessmentModel(input_size=7)
        self.scaler = StandardScaler()
        self.patient_thresholds = {}
        self.alert_history = {}
        self.mlflow_experiment = "health_monitoring"
        self._setup_mlflow()
    
    def _setup_mlflow(self):
        mlflow.set_experiment(self.mlflow_experiment)
        self.model_version = mlflow.register_model(
            model_uri=f"runs:/{mlflow.active_run().info.run_id}/model",
            name="health_risk_model"
        )
    
    def load_patient_data(self, patient_id: str, data_path: str = "data/synthetic_health_data.json") -> List[HealthData]:
        """Load patient data from JSON file."""
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        patient_data = []
        for record in data:
            if record['patient_id'] == patient_id:
                health_data = HealthData(
                    patient_id=record['patient_id'],
                    timestamp=datetime.fromisoformat(record['timestamp']),
                    heart_rate=record.get('heart_rate'),
                    systolic=record.get('systolic'),
                    diastolic=record.get('diastolic'),
                    blood_glucose=record.get('blood_glucose'),
                    spo2=record.get('spo2'),
                    sleep=record.get('sleep'),
                    activity=record.get('activity'),
                    mood=record.get('mood'),
                    metadata=record.get('metadata')
                )
                patient_data.append(health_data)
        
        return sorted(patient_data, key=lambda x: x.timestamp)
    
    def update_patient_thresholds(self, patient_id: str, historical_data: List[HealthData]):
        """Update patient-specific thresholds based on historical data."""
        if patient_id not in self.patient_thresholds:
            self.patient_thresholds[patient_id] = {}
        
        # Calculate baseline metrics
        heart_rates = [d.heart_rate for d in historical_data if d.heart_rate is not None]
        blood_glucose = [d.blood_glucose for d in historical_data if d.blood_glucose is not None]
        spo2_levels = [d.spo2 for d in historical_data if d.spo2 is not None]
        
        if heart_rates:
            self.patient_thresholds[patient_id]['heart_rate'] = {
                'mean': np.mean(heart_rates),
                'std': np.std(heart_rates)
            }
        
        if blood_glucose:
            self.patient_thresholds[patient_id]['blood_glucose'] = {
                'mean': np.mean(blood_glucose),
                'std': np.std(blood_glucose)
            }
        
        if spo2_levels:
            self.patient_thresholds[patient_id]['spo2'] = {
                'mean': np.mean(spo2_levels),
                'std': np.std(spo2_levels)
            }
    
    def assess_risk(self, data: HealthData, historical_data: List[HealthData]) -> Tuple[float, str]:
        """Assess health risk using both rule-based and ML approaches."""
        risk_score = 0.0
        explanation = []
        
        # Rule-based assessment
        if data.heart_rate is not None:
            if data.heart_rate > 100:
                risk_score += 0.3
                explanation.append("Elevated heart rate")
            elif data.heart_rate < 60:
                risk_score += 0.2
                explanation.append("Low heart rate")
        
        if data.blood_glucose is not None:
            if data.blood_glucose > 180:
                risk_score += 0.4
                explanation.append("High blood glucose")
            elif data.blood_glucose < 70:
                risk_score += 0.5
                explanation.append("Low blood glucose")
        
        if data.spo2 is not None and data.spo2 < 95:
            risk_score += 0.3
            explanation.append("Low blood oxygen")
        
        # ML-based assessment
        if len(historical_data) >= 10:
            dataset = HealthDataset(historical_data + [data])
            with torch.no_grad():
                sequence = dataset[0].unsqueeze(0)
                ml_risk = self.model(sequence).item()
                risk_score = 0.7 * risk_score + 0.3 * ml_risk
        
        return min(risk_score, 1.0), " and ".join(explanation) if explanation else "No significant risks detected"
    
    def generate_alert(self, risk_score: float, explanation: str, data: HealthData) -> Alert:
        """Generate appropriate alert based on risk assessment."""
        if risk_score >= 0.7:
            return Alert(
                level="severe",
                message=f"Severe health risk detected: {explanation}",
                action_required=True,
                escalation_needed=True,
                explanation=explanation,
                timestamp=data.timestamp,
                confidence=risk_score
            )
        elif risk_score >= 0.4:
            return Alert(
                level="mild",
                message=f"Moderate health risk detected: {explanation}",
                action_required=True,
                escalation_needed=False,
                explanation=explanation,
                timestamp=data.timestamp,
                confidence=risk_score
            )
        else:
            return Alert(
                level="none",
                message="No significant health risks detected",
                action_required=False,
                escalation_needed=False,
                explanation=explanation,
                timestamp=data.timestamp,
                confidence=1 - risk_score
            )
    
    def check_bias(self, data: HealthData, historical_data: List[HealthData]) -> bool:
        """Check for potential bias in risk assessment."""
        # Implement bias detection logic here
        # For now, return True if no bias detected
        return True
    
    def invoke(self, state: AgentState) -> AgentState:
        """Process new health data and update agent state."""
        # Update patient thresholds if needed
        if state.patient_thresholds is None:
            self.update_patient_thresholds(state.current_data.patient_id, state.historical_data)
            state.patient_thresholds = self.patient_thresholds
        
        # Assess risk
        risk_score, explanation = self.assess_risk(state.current_data, state.historical_data)
        
        # Check for bias
        if not self.check_bias(state.current_data, state.historical_data):
            explanation += " (Bias detected in assessment)"
        
        # Generate alert
        alert = self.generate_alert(risk_score, explanation, state.current_data)
        
        # Update state
        state.risk_score = risk_score
        state.alerts.append(alert)
        state.historical_data.append(state.current_data)
        
        # Log to MLflow
        with mlflow.start_run():
            mlflow.log_metric("risk_score", risk_score)
            mlflow.log_param("alert_level", alert.level)
            mlflow.log_param("patient_id", state.current_data.patient_id)
        
        return state

def create_health_agent() -> HealthAgent:
    """Create and initialize a new health agent."""
    return HealthAgent()

# Example usage
if __name__ == "__main__":
    # Create sample data
    current_data = HealthData(
        patient_id="P001",
        timestamp=datetime.now(),
        heart_rate=85,
        systolic=130,
        diastolic=85,
        blood_glucose=120,
        spo2=97,
        sleep=7.5,
        activity=6000,
        mood="Good"
    )
    
    # Create agent state
    state = AgentState(
        current_data=current_data,
        historical_data=[],
        alerts=[],
        risk_score=0.0
    )
    
    # Create and run the agent
    agent = create_health_agent()
    result = agent.invoke(state)
    
    # Print results
    print(f"Risk Score: {result.risk_score}")
    print(f"Latest Alert: {result.alerts[-1]}") 