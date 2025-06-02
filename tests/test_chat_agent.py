import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from agent.chat_agent import chat_with_agent

def create_test_report():
    """Create a test health report for the chat agent to analyze."""
    test_report = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "heart_rate": 75,
            "blood_glucose": 120,
            "spo2": 98,
            "systolic": 120,
            "diastolic": 80,
            "sleep_duration": 7.5,
            "activity_level": 8000
        },
        "risk_score": 0.2,
        "alerts": []
    }
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    # Save the test report
    with open("reports/test_report.json", "w") as f:
        json.dump(test_report, f, indent=2)

def main():
    """Main function to run the chat agent test with hard-coded questions."""
    print("🤖 Health Monitoring Chat Agent Test (Automated)")
    print("==============================================")
    
    # Create a test report
    create_test_report()
    
    test_questions = [
        "What is my blood glucose level?",
        "What is the current heart rate?",
        "Is the blood glucose level normal?",
        "What is the risk score?",
        "Are there any health alerts?",
        "Show me the latest health metrics.",
        "What is the highest heart rate recorded?",
        "Is there any concerning trend in the data?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\nTest {i}: {question}")
        try:
            response = chat_with_agent(question)
            print(f"Assistant: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 