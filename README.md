# LouBot AI - Advanced AI-Powered Drone Assistant

**LouBot AI** is a comprehensive AI-powered drone assistant that combines natural language processing, computer vision, drone control, and advanced authentication systems. Built with Django, AIML, YOLO object detection, and WebAuthn biometric authentication.

## Key Features

### **AI Chatbot System**
- **AIML-based Natural Language Processing** with 100+ knowledge files
- **Multi-language Support** (English, Urdu with real-time translation)
- **Contextual Memory System** (Episodic, Semantic, and Social Memory)
- **Sentiment Analysis** for conversation understanding
- **Dynamic Response Processing** with real-time data integration

### **Computer Vision & Object Detection**
- **YOLOv8 Integration** for real-time object detection
- **80+ Object Classes** recognition (people, vehicles, animals, objects)
- **Live Video Streaming** with detection overlays
- **Detection Bridge System** for AI chat integration
- **Configurable Detection Settings** (confidence, model selection)

### **Advanced Drone Control**
- **DJI Tello Integration** with full flight control
- **Voice Commands** for drone operations
- **Real-time Sensor Monitoring** (battery, temperature, altitude, speed)
- **Automatic Safety Checks** and connection management
- **Movement Commands** (forward, backward, left, right, takeoff, land)

### **Biometric Authentication**
- **WebAuthn Face ID/Touch ID** support for macOS
- **Secure Credential Management** with cryptography
- **One-tap Login** with biometric verification
- **Fallback Authentication** with traditional email/password

### **Memory Systems**
- **Episodic Memory**: Conversation history and personal events
- **Semantic Memory**: Knowledge facts and learned information  
- **Social Memory**: User relationships and social network
- **Sensory Memory**: Real-time sensor data and visual perceptions

### **Web Interface**
- **Modern Responsive Design** with Bootstrap and custom CSS
- **Real-time Chat Interface** with dynamic responses
- **Drone Video Feed** with object detection overlay
- **YOLO Management Dashboard** for detection configuration
- **User Profile Management** with gender detection

## Project Structure

LouBot-AI/
├── Memory/                    # Main Django App (AI & Authentication)
│   ├── aiml.py               # AIML kernel initialization
│   ├── webauthn_utils.py     # Biometric authentication
│   ├── gender_names_db.py    # Name-based gender detection
│   ├── detection_bridge.py   # YOLO-AIML integration bridge
│   ├── Emails.py             # Email notification system
│   ├── OTP.py                # Password reset system
│   ├── Speech.py             # Speech-to-text processing
│   ├── Social_Network.py     # Social memory management
│   ├── nlp.py                # Natural language processing
│   └── prolog.py             # Knowledge graph processing
├── Sensory_Memory/           # Drone & Vision System
│   ├── yolo_detector.py      # YOLOv8 object detection
│   ├── detection_config.py   # Detection configuration
│   └── views.py              # Drone control & video streaming
├── Data/                     # AIML Knowledge Files (100+ files)
│   ├── semantic_memory.aiml  # Knowledge facts
│   ├── social_memory.aiml    # Social interactions
│   ├── episodic_memory.aiml  # Conversation history
│   ├── sensory_memory.aiml   # Visual & sensor data
│   ├── custom_drone.aiml     # Drone control commands
│   └── ... (90+ more knowledge files)
├── templates/                # HTML Templates
├── static/                   # CSS, JS, Images
├── media/                    # User uploads
└── yolov8n.pt               # YOLOv8 model file
```

## 🛠️ Technology Stack

### **Backend**
- **Django 5.0.3** - Web framework
- **Neo4j** - Graph database for relationships
- **SQLite** - Relational database
- **AIML** - Natural language processing
- **YOLOv8** - Object detection

### **AI & ML**
- **Ultralytics 8.2.31** - YOLO implementation
- **OpenCV 4.10.0** - Computer vision
- **NLTK 3.8.1** - Natural language toolkit
- **SpaCy 3.7.4** - NLP processing
- **Transformers 4.41.2** - Language models

### **Authentication & Security**
- **WebAuthn** - Biometric authentication
- **Cryptography 42.0.8** - Security utilities
- **CBOR2 5.6.4** - Data serialization

### **Drone Control**
- **DJITelloPy 2.5.0** - DJI Tello SDK
- **SpeechRecognition 3.10.1** - Voice commands

### **Frontend**
- **Bootstrap** - Responsive design
- **JavaScript** - Dynamic interactions
- **WebAuthn API** - Biometric integration

## Installation & Setup

### **Prerequisites**
- Python 3.8+
- Conda environment manager
- Neo4j Desktop (for graph database)
- DJI Tello drone (optional, for drone features)

### **1. Environment Setup**
```bash
# Create and activate conda environment
conda create -n LouBot python=3.8
conda activate LouBot

# Clone the repository
git clone <repository-url>
cd LouBot-AI
```

### **2. Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm
```

### **3. Neo4j Configuration**
- Install Neo4j Desktop
- Create new project with local DBMS
- Set credentials: `username=neo4j, password=12345678`
- Start the database

### **4. Run the Application**
```bash
# Start Django development server
python manage.py runserver

# Access the application
# Open browser: http://localhost:8000
```

## Usage Guide

### **Getting Started**
1. **Register Account**: Create new account with email/password
2. **Setup Biometric Auth**: Enable Face ID/Touch ID for quick login
3. **Access Chat Interface**: Start conversing with LouBot AI

### **AI Chat Features**
- **Natural Conversations**: Chat naturally about any topic
- **Memory Recall**: Ask about previous conversations
- **Knowledge Queries**: Learn new facts and information
- **Social Network**: Manage relationships and connections

### **Drone Control** (requires DJI Tello)
- **Voice Commands**: "Take off", "Land", "Move forward 50"
- **Visual Feedback**: Real-time video with object detection
- **Sensor Monitoring**: Battery, temperature, altitude status
- **Safety Features**: Automatic battery checks and connection management

### **Object Detection**
- **Real-time Detection**: See objects in drone video feed
- **AI Integration**: Ask "What can you see?" or "Do you see a person?"
- **Configuration**: Adjust detection sensitivity and model selection
- **Management Dashboard**: Enable/disable and configure detection

### **Biometric Authentication**
- **Setup**: Register Face ID/Touch ID after login
- **Quick Login**: One-tap authentication
- **Security**: Cryptographically secure credential storage
- **Fallback**: Traditional email/password always available

## Configuration

### **YOLO Detection Settings**
```python
# In Sensory_Memory/detection_config.py
ENABLE_YOLO_DETECTION = True
YOLO_MODEL_PATH = 'yolov8n.pt'  # or yolov8s.pt, yolov8m.pt, etc.
YOLO_CONFIDENCE_THRESHOLD = 0.5
DETECTION_INTERVAL = 1  # Process every frame
```

### **AIML Knowledge Base**
- **100+ Knowledge Files**: Located in `Data/` directory
- **Custom Patterns**: Add new conversation patterns
- **Dynamic Responses**: Real-time data integration
- **Multi-language**: English and Urdu support

### **Database Configuration**
- **Neo4j**: Graph database for relationships
- **SQLite**: Relational data storage
- **Session Management**: User session handling

## Features Overview

| Feature | Status | Description |
|---------|--------|-------------|
| AI Chatbot | ✅ Complete | AIML-based with 100+ knowledge files |
| Object Detection | ✅ Complete | YOLOv8 with 80+ object classes |
| Drone Control | ✅ Complete | Full DJI Tello integration |
| Biometric Auth | ✅ Complete | Face ID/Touch ID support |
| Memory Systems | ✅ Complete | Episodic, Semantic, Social memory |
| Multi-language | ✅ Complete | English/Urdu with translation |
| Voice Commands | ✅ Complete | Speech-to-text integration |
| Real-time Video | ✅ Complete | Live streaming with detection |
| Web Interface | ✅ Complete | Modern responsive design |
| Email System | ✅ Complete | Notifications and OTP |

## Interface Screenshots

### **Main Chat Interface**
- Real-time conversation with AI
- Dynamic response processing
- Memory integration
- Multi-language support

### **Drone Video Feed**
- Live video streaming
- Object detection overlays
- Real-time sensor data
- YOLO management controls

### **Biometric Setup**
- Face ID/Touch ID registration
- Secure credential management
- One-tap authentication
- Fallback options

## 🔒 Security Features

- **WebAuthn Biometric Authentication**
- **Cryptographic Credential Storage**
- **Session Management**
- **CSRF Protection**
- **Secure Password Reset**
- **Email Verification**

## Drone Integration

### **Supported Commands**
- **Takeoff/Landing**: "Take off", "Land"
- **Movement**: "Move forward 50", "Move left 30"
- **Status**: "Battery status", "What's my height?"
- **Visual**: "What can you see?", "Do you see a person?"

### **Safety Features**
- **Battery Monitoring**: Automatic low-battery warnings
- **Connection Management**: Automatic reconnection
- **Error Handling**: Graceful failure recovery
- **Flight Status**: Real-time flying state tracking

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## Acknowledgments

- **DJI Tello** for drone SDK
- **Ultralytics** for YOLOv8 implementation
- **AIML Community** for natural language processing
- **Neo4j** for graph database technology
- **WebAuthn** for biometric authentication standards

---

**LouBot AI** - Where AI meets the sky!







