# MongoDB Import Test

## Successful Connection and Data Import

We successfully connected to a remote MongoDB Atlas cluster using environment variables loaded from a `.env` file and the `python-dotenv` package. The import script (`import_to_mongo_db.py`) was used to load health data from a JSON file into the database.

### Steps Performed
1. Set up the `.env` file with the following variables:
   ```
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
   MONGODB_DB_NAME=health_monitoring
   MONGODB_COLLECTION_NAME=health_data
   ```
2. Ran the import script:
   ```bash
   python tests/import_to_mongo_db.py
   ```
3. Output confirmed:
   - Successful connection to MongoDB
   - 10,085 records imported
   - Indexes created on `patient_id` and `timestamp`
   - Collection statistics displayed

### Example Output
```
Successfully connected to MongoDB!
Successfully imported 10085 records
Created indexes on patient_id, timestamp

Collection Statistics:
Total documents: 30255
Unique patients: 5
Date range: 2025-05-26T14:50:54.888774 to 2025-06-02T14:50:54.888774

MongoDB connection closed
```

---

This demonstrates that the system is able to connect to a remote MongoDB instance, import data, and report statistics as expected. 