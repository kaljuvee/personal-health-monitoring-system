from pymongo import MongoClient
import json
import os
from datetime import datetime
import argparse
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

def connect_to_mongodb(connection_string: str = MONGODB_URI):
    """Connect to MongoDB and return database and collection objects."""
    try:
        client = MongoClient(connection_string)
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Get database and collection
        db = client[MONGODB_DB_NAME]
        collection = db[MONGODB_COLLECTION_NAME]
        
        return client, db, collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def import_data(collection, data_file: str):
    """Import data from JSON file to MongoDB collection."""
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
            
        # Add import metadata
        for record in data:
            record['imported_at'] = datetime.now().isoformat()
        
        # Insert data
        result = collection.insert_many(data)
        print(f"Successfully imported {len(result.inserted_ids)} records")
        
        # Create indexes
        collection.create_index([("patient_id", 1), ("timestamp", 1)])
        collection.create_index("timestamp")
        print("Created indexes on patient_id, timestamp")
        
    except Exception as e:
        print(f"Error importing data: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Import health data to MongoDB')
    parser.add_argument('--file', default='data/synthetic_health_data.json',
                      help='Path to JSON data file')
    parser.add_argument('--uri', default=MONGODB_URI,
                      help='MongoDB connection string')
    
    args = parser.parse_args()
    
    # Check if data file exists
    if not os.path.exists(args.file):
        print(f"Error: Data file {args.file} not found")
        return
    
    # Connect to MongoDB
    client, db, collection = connect_to_mongodb(args.uri)
    
    try:
        # Import data
        import_data(collection, args.file)
        
        # Print collection statistics
        print("\nCollection Statistics:")
        print(f"Total documents: {collection.count_documents({})}")
        print(f"Unique patients: {len(collection.distinct('patient_id'))}")
        print(f"Date range: {collection.find_one(sort=[('timestamp', 1)])['timestamp']} to {collection.find_one(sort=[('timestamp', -1)])['timestamp']}")
        
    finally:
        # Close the connection
        client.close()
        print("\nMongoDB connection closed")

if __name__ == "__main__":
    main() 