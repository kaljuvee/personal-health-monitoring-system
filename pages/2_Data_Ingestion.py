import streamlit as st
import pandas as pd
import json
import os
import requests
from datetime import datetime
from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

st.set_page_config(page_title="Data Ingestion", page_icon="📥", layout="wide")

st.title("📥 Health Data Ingestion")
st.markdown("Import health data from local files or remote sources")

data = None  # Ensure data is always defined

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

def validate_data(data):
    """Validate the structure and content of the data."""
    if not isinstance(data, list):
        st.error("Data must be a list of records")
        return False
    
    if not data:
        st.error("No records found in the data")
        return False
    
    # Check if each record is a dictionary
    if not all(isinstance(record, dict) for record in data):
        st.error("Each record must be a dictionary")
        return False
    
    # Check required fields
    required_fields = ["patient_id", "timestamp"]
    missing_fields = []
    for field in required_fields:
        if not all(field in record for record in data):
            missing_fields.append(field)
    
    if missing_fields:
        st.error(f"Missing required fields: {', '.join(missing_fields)}")
        return False
    
    # Check timestamp format
    try:
        for record in data:
            if not isinstance(record["timestamp"], str):
                st.error("Timestamp must be a string")
                return False
            # Try to parse the timestamp
            datetime.fromisoformat(record["timestamp"])
    except ValueError:
        st.error("Invalid timestamp format. Expected ISO format (YYYY-MM-DDTHH:MM:SS)")
        return False
    
    return True

# Data source selection
data_source = st.radio(
    "Select Data Source",
    ["Local File", "Remote URL"],
    horizontal=True
)

if data_source == "Local File":
    # Local file selection
    data_dir = "data"
    default_file = "test_health_data.json"
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        default_index = files.index(default_file) if default_file in files else 0
        selected_file = st.selectbox(
            "Select a JSON file",
            files,
            index=default_index,
            format_func=lambda x: f"{x} ({os.path.getsize(os.path.join(data_dir, x)) / 1024:.1f} KB)"
        )
        
        if selected_file:
            file_path = os.path.join(data_dir, selected_file)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                st.error("Invalid JSON file")
                data = None
    else:
        st.warning("No data directory found. Please generate data first.")
        data = None

else:  # Remote URL
    # Remote URL input
    url = st.text_input("Enter Remote URL")
    username = st.text_input("Username (optional)")
    password = st.text_input("Password (optional)", type="password")
    
    if url:
        try:
            auth = (username, password) if username and password else None
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            st.error(f"Failed to fetch data from URL: {str(e)}")
            data = None

# Data validation and preview
if data:
    if validate_data(data):
        st.subheader("Data Preview")
        
        # Convert to DataFrame for easier display
        df = pd.DataFrame(data)
        
        # Basic validation results
        st.write("Data Validation:")
        validation_results = {
            "Total Records": len(data),
            "Required Fields": all(field in record for record in data for field in ["patient_id", "timestamp"]),
            "Timestamp Format": all(isinstance(record["timestamp"], str) for record in data),
            "Patient IDs": len(set(record["patient_id"] for record in data))
        }
        
        for key, value in validation_results.items():
            st.write(f"- {key}: {'✅' if value else '❌'}")
        
        # Show data preview
        st.dataframe(df.head())
        
        # Data statistics
        st.subheader("Data Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(data))
        with col2:
            st.metric("Unique Patients", len(set(record["patient_id"] for record in data)))
        with col3:
            if "timestamp" in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                date_range = f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}"
                st.metric("Date Range", date_range)

        # Import to MongoDB
        if st.button("Import to MongoDB"):
            client = get_mongodb_connection()
            if client:
                try:
                    db = client[MONGODB_DB_NAME]
                    collection = db[MONGODB_COLLECTION_NAME]
                    
                    # Add import metadata
                    for record in data:
                        record['imported_at'] = datetime.now().isoformat()
                    
                    # Insert data
                    result = collection.insert_many(data)
                    
                    # Create indexes
                    collection.create_index([("patient_id", 1), ("timestamp", 1)])
                    collection.create_index("timestamp")
                    
                    st.success(f"Successfully imported {len(result.inserted_ids)} records to MongoDB")
                    
                    # Show collection statistics
                    st.subheader("Collection Statistics")
                    st.write(f"Total documents: {collection.count_documents({})}")
                    st.write(f"Unique patients: {len(collection.distinct('patient_id'))}")
                    
                except Exception as e:
                    st.error(f"Failed to import data: {str(e)}")
                finally:
                    client.close() 