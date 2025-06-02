import sys
import os
import json
from datetime import datetime, timedelta
import time
import threading
import numpy as np
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from agent.health_agent import create_health_agent, HealthData, AgentState

def save_test_log(data: list, filename: str = None):
    """Save test results to a JSON report file with timestamp."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/report_{timestamp}.json"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_results": data
        }, f, indent=2)
    print(f"\nTest results saved to {filename}")

def generate_test_data(patient_id: str, num_records: int = 10) -> list:
    """Generate test data for a single patient."""
    data = []
    base_time = datetime.now()
    
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
    
    for i in range(num_records):
        timestamp = base_time + timedelta(minutes=i)
        
        # Occasionally introduce anomalies
        if i == 3:  # Simulate high heart rate
            heart_rate = baseline["heart_rate"] + 30
        elif i == 6:  # Simulate low blood glucose
            blood_glucose = baseline["blood_glucose"] - 40
        else:
            heart_rate = max(40, min(200, np.random.normal(baseline["heart_rate"], 5)))
            blood_glucose = max(50, min(300, np.random.normal(baseline["blood_glucose"], 10)))
        
        record = {
            "patient_id": patient_id,
            "timestamp": timestamp.isoformat(),
            "heart_rate": heart_rate,
            "systolic": max(80, min(200, np.random.normal(baseline["systolic"], 5))),
            "diastolic": max(50, min(120, np.random.normal(baseline["diastolic"], 5))),
            "blood_glucose": blood_glucose,
            "spo2": max(90, min(100, np.random.normal(baseline["spo2"], 0.5))),
            "sleep": max(0, min(12, np.random.normal(baseline["sleep"], 1))),
            "activity": max(0, min(20000, np.random.normal(baseline["activity"], 1000))),
            "mood": np.random.choice(["happy", "neutral", "stressed", "tired"]),
            "metadata": {
                "source": "test",
                "generated_at": datetime.now().isoformat()
            }
        }
        data.append(record)
    
    return data

def save_test_data(data: list, filename: str = "reports/test_health_data.json"):
    """Save test data to JSON file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def background_monitoring(agent, patient_id: str, stop_event: threading.Event):
    """Background thread for continuous monitoring."""
    print(f"\nStarting background monitoring for patient {patient_id}")
    test_results = []
    
    while not stop_event.is_set():
        try:
            # Generate new data point
            new_data = generate_test_data(patient_id, num_records=1)[0]
            
            # Create health data object
            health_data = HealthData(
                patient_id=new_data["patient_id"],
                timestamp=datetime.fromisoformat(new_data["timestamp"]),
                heart_rate=new_data.get("heart_rate"),
                systolic=new_data.get("systolic"),
                diastolic=new_data.get("diastolic"),
                blood_glucose=new_data.get("blood_glucose"),
                spo2=new_data.get("spo2"),
                sleep=new_data.get("sleep"),
                activity=new_data.get("activity"),
                mood=new_data.get("mood"),
                metadata=new_data.get("metadata")
            )
            
            # Create agent state
            state = AgentState(
                current_data=health_data,
                historical_data=[],
                alerts=[],
                risk_score=0.0
            )
            
            # Process data
            result = agent.invoke(state)
            
            # Store results
            test_result = {
                "timestamp": new_data["timestamp"],
                "metrics": {
                    "heart_rate": new_data["heart_rate"],
                    "blood_glucose": new_data["blood_glucose"],
                    "risk_score": result.risk_score
                },
                "alert": {
                    "level": result.alerts[-1].level if result.alerts else "none",
                    "message": result.alerts[-1].message if result.alerts else "No alerts"
                }
            }
            test_results.append(test_result)
            
            # Print results
            print(f"\nTimestamp: {new_data['timestamp']}")
            print(f"Heart Rate: {new_data['heart_rate']:.1f} bpm")
            print(f"Blood Glucose: {new_data['blood_glucose']:.1f} mg/dL")
            print(f"Risk Score: {result.risk_score:.2f}")
            if result.alerts:
                alert = result.alerts[-1]
                print(f"Alert: {alert.level.upper()} - {alert.message}")
                print(f"Action Required: {alert.action_required}")
                print(f"Escalation Needed: {alert.escalation_needed}")
            
            # Save results after each iteration
            save_test_log(test_results)
            
            # Wait for 1 minute
            time.sleep(60)
        except Exception as e:
            print(f"Error in background monitoring: {e}")
            break
    
    return test_results

def main():
    # Create health agent
    agent = create_health_agent()
    
    # Generate initial test data
    test_data = generate_test_data("P001", num_records=10)
    save_test_data(test_data)
    
    # Process initial data
    print("\nProcessing initial test data...")
    initial_results = []
    for record in test_data:
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
        
        result = agent.invoke(state)
        
        # Store results
        test_result = {
            "timestamp": record["timestamp"],
            "metrics": {
                "heart_rate": record["heart_rate"],
                "blood_glucose": record["blood_glucose"],
                "risk_score": result.risk_score
            },
            "alert": {
                "level": result.alerts[-1].level if result.alerts else "none",
                "message": result.alerts[-1].message if result.alerts else "No alerts"
            }
        }
        initial_results.append(test_result)
        
        print(f"\nTimestamp: {record['timestamp']}")
        print(f"Heart Rate: {record['heart_rate']:.1f} bpm")
        print(f"Blood Glucose: {record['blood_glucose']:.1f} mg/dL")
        print(f"Risk Score: {result.risk_score:.2f}")
        if result.alerts:
            alert = result.alerts[-1]
            print(f"Alert: {alert.level.upper()} - {alert.message}")
    
    # Save initial results
    save_test_log(initial_results)
    
    # Start background monitoring
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=background_monitoring,
        args=(agent, "P001", stop_event)
    )
    monitor_thread.start()
    
    try:
        # Run for 5 minutes
        print("\nStarting continuous monitoring for 5 minutes...")
        time.sleep(300)
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    finally:
        stop_event.set()
        monitor_thread.join(timeout=5)  # Wait up to 5 seconds for thread to finish

if __name__ == "__main__":
    main() 