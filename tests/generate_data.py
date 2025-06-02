import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any

def generate_health_data(
    start_date: datetime,
    end_date: datetime,
    frequency_minutes: int,
    num_patients: int,
    metrics: List[str]
) -> List[Dict[str, Any]]:
    """
    Generate synthetic health data in a format suitable for MongoDB.
    
    Args:
        start_date: Start date for data generation
        end_date: End date for data generation
        frequency_minutes: Data collection frequency in minutes
        num_patients: Number of patients to generate data for
        metrics: List of health metrics to generate
    
    Returns:
        List of dictionaries containing health data records
    """
    # Generate timestamps
    timestamps = pd.date_range(start=start_date, end=end_date, freq=f"{frequency_minutes}T")
    
    # Initialize empty list to store all patient data
    all_data = []
    
    for patient_id in range(1, num_patients + 1):
        # Generate base values for each metric
        base_values = {
            "Heart Rate": np.random.normal(75, 5),
            "Blood Pressure": {
                "systolic": np.random.normal(120, 5),
                "diastolic": np.random.normal(80, 5)
            },
            "Blood Glucose": np.random.normal(100, 10),
            "SpO2": np.random.normal(98, 0.5),
            "Sleep": np.random.normal(7, 1),
            "Activity": np.random.normal(5000, 1000),
            "Mood": np.random.choice(["Good", "Fair", "Poor"], p=[0.6, 0.3, 0.1])
        }
        
        # Generate data for each timestamp
        for timestamp in timestamps:
            data_point = {
                "patient_id": f"P{patient_id:03d}",
                "timestamp": timestamp.isoformat(),
                "metadata": {
                    "source": "synthetic",
                    "version": "1.0",
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            # Add selected metrics
            for metric in metrics:
                if metric == "Blood Pressure":
                    data_point["vitals"] = {
                        "systolic": float(base_values[metric]["systolic"] + np.random.normal(0, 2)),
                        "diastolic": float(base_values[metric]["diastolic"] + np.random.normal(0, 2))
                    }
                else:
                    metric_key = metric.lower().replace(" ", "_")
                    if metric == "Mood":
                        data_point[metric_key] = base_values[metric]
                    else:
                        data_point[metric_key] = float(base_values[metric] + np.random.normal(0, 2))
            
            all_data.append(data_point)
    
    return all_data

def save_data_to_json(data: List[Dict[str, Any]], filename: str):
    """Save generated data to a JSON file."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    # Configuration
    config = {
        "start_date": datetime.now() - timedelta(days=7),
        "end_date": datetime.now(),
        "frequency_minutes": 5,
        "num_patients": 5,
        "metrics": ["Heart Rate", "Blood Pressure", "Blood Glucose", "SpO2", "Sleep", "Activity", "Mood"]
    }
    
    # Generate data
    print("Generating synthetic health data...")
    health_data = generate_health_data(
        config["start_date"],
        config["end_date"],
        config["frequency_minutes"],
        config["num_patients"],
        config["metrics"]
    )
    
    # Save to JSON
    output_file = "data/synthetic_health_data.json"
    save_data_to_json(health_data, output_file)
    print(f"Data saved to {output_file}")
    
    # Print sample of generated data
    print("\nSample of generated data:")
    print(json.dumps(health_data[0], indent=2))
    
    # Print statistics
    print(f"\nGenerated {len(health_data)} records")
    print(f"Time range: {config['start_date']} to {config['end_date']}")
    print(f"Number of patients: {config['num_patients']}")
    print(f"Metrics included: {', '.join(config['metrics'])}")

if __name__ == "__main__":
    main() 