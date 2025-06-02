# Personal Health Monitoring System (PHMS)

An AI-powered health monitoring system that provides real-time risk assessment and personalized interventions for patients with chronic illnesses.

## 🏥 Overview

The Personal Health Monitoring System (PHMS) is a comprehensive solution that leverages AI to monitor patient health data in real-time, detect potential health risks, and provide timely interventions. The system integrates data from various sources including wearable devices, Electronic Health Records (EHR), and behavioral patterns.

## 🌟 Key Features

- **Real-time Health Monitoring**
  - Continuous tracking of vital signs
  - Integration with wearable devices
  - Behavioral pattern analysis

- **AI-Powered Risk Assessment**
  - Personalized risk scoring
  - Early warning system
  - Continuous learning and adaptation

- **Smart Intervention System**
  - Automated health alerts
  - Behavioral recommendations
  - Care provider escalation

- **Data Privacy & Security**
  - HIPAA-compliant data handling
  - Secure data storage
  - User consent management

## 🛠️ Technical Architecture

### Components

1. **Data Generation & Ingestion**
   - Synthetic data generation for testing
   - Real-time data ingestion from wearables
   - EHR data integration

2. **Risk Assessment Engine**
   - Hybrid ML models (rule-based + deep learning)
   - Real-time anomaly detection
   - Personalized threshold management

3. **Alert Management System**
   - Multi-level alert system
   - Customizable intervention rules
   - Care provider integration

4. **Analytics Dashboard**
   - Real-time monitoring
   - Historical trend analysis
   - Performance metrics

### Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MongoDB
- **ML Framework**: PyTorch/TensorFlow
- **MLOps**: MLflow
- **Cloud**: Azure

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB
- Required Python packages (see requirements.txt)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/personal-health-monitoring-system.git
   cd personal-health-monitoring-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install MongoDB:

   **Ubuntu/Debian:**
   ```bash
   # Import MongoDB public GPG key
   curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
      sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
      --dearmor

   # Create list file for MongoDB
   echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

   # Update package list
   sudo apt-get update

   # Install MongoDB
   sudo apt-get install -y mongodb-org

   # Start MongoDB
   sudo systemctl start mongod

   # Enable MongoDB to start on boot
   sudo systemctl enable mongod
   ```

   **macOS (using Homebrew):**
   ```bash
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community
   ```

   **Windows:**
   - Download MongoDB Community Server from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Run the installer
   - Follow the installation wizard
   - MongoDB will be installed as a Windows service and started automatically

5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. Run the application:
   ```bash
   streamlit run Home.py
   ```

### Data Generation and Import

1. Generate synthetic health data:
   ```bash
   python tests/generate_data.py
   ```

2. Import data into MongoDB:
   ```bash
   python tests/import_to_mongo_db.py
   ```

   Optional arguments:
   ```bash
   python tests/import_to_mongo_db.py --file path/to/data.json --uri mongodb://your-connection-string
   ```

## 📊 System Pages

1. **Data Generation** (`/pages/1_Data_Generation.py`)
   - Generate synthetic health data
   - Configure data parameters
   - Preview generated data

2. **Data Ingestion** (`/pages/2_Data_Ingestion.py`)
   - Configure data sources
   - Monitor data flow
   - Data validation

3. **Risk Assessment** (`/pages/3_Risk_Assessment.py`)
   - View risk scores
   - Configure assessment parameters
   - Model performance metrics

4. **Alert Management** (`/pages/4_Alert_Management.py`)
   - Configure alert rules
   - View alert history
   - Manage escalation paths

5. **User Settings** (`/pages/5_User_Settings.py`)
   - Personalize monitoring parameters
   - Configure privacy settings
   - Manage notifications

6. **Analytics Dashboard** (`/pages/6_Analytics_Dashboard.py`)
   - View health trends
   - System performance metrics
   - User engagement statistics

## 🔒 Security & Privacy

- All data is encrypted at rest and in transit
- HIPAA-compliant data handling
- Role-based access control
- Regular security audits
- User consent management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Healthcare professionals who provided domain expertise
- Open-source community for various tools and libraries
- Contributors and maintainers of the project