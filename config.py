from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://<username>:<password>@<cluster>.mongodb.net/')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'health_monitoring')
MONGODB_COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME', 'health_data') 