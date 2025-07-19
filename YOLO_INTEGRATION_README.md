# 🤖 YOLOv8 Object Detection Integration for LouBot

This integration adds seamless YOLOv8 object detection capabilities to the LouBot drone video streaming system. The integration is designed to be **modular and easily removable** without affecting the core functionality.

## 🚀 Features

- **Real-time Object Detection**: YOLOv8 detection on live drone video feed
- **Web-based Management**: Easy enable/disable via web interface
- **Multiple Model Support**: Choose from YOLOv8n (fast) to YOLOv8x (accurate)
- **Configurable Settings**: Adjust confidence threshold and detection intervals
- **Seamless Integration**: Works with existing drone streaming without modifications
- **Easy Removal**: Can be disabled/removed without breaking existing functionality

## 📦 Installation

### 1. Install YOLOv8 Dependencies

```bash
# Activate your conda environment
conda activate LouBot

# Install ultralytics (YOLOv8)
pip install ultralytics==8.2.31
```

### 2. Verify Installation

The system will automatically download the YOLO model on first use. The default model (`yolov8n.pt`) is about 6MB.

## 🎯 Usage

### Quick Start

1. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Access the management interface:**
   - Navigate to: `http://localhost:8000/Sensory_Memory/yolo_management/`
   - Or use the API endpoints directly

3. **View live detection:**
   - Go to: `http://localhost:8000/Sensory_Memory/drone_video_feed/`
   - If YOLO is enabled, you'll see bounding boxes and labels on detected objects

### Configuration Options

#### Enable/Disable Detection
```python
# In Sensory_Memory/detection_config.py
ENABLE_YOLO_DETECTION = True  # Set to False to disable
```

#### Model Selection
- `yolov8n.pt` - Nano (fastest, ~6MB)
- `yolov8s.pt` - Small (~22MB)
- `yolov8m.pt` - Medium (~52MB)
- `yolov8l.pt` - Large (~110MB)
- `yolov8x.pt` - Extra Large (best accuracy, ~220MB)

#### Confidence Threshold
- Range: 0.1 - 0.9
- Default: 0.5
- Higher values = fewer but more confident detections

## 🌐 Web Management Interface

Access the management interface at `/Sensory_Memory/yolo_management/`

### Features:
- **Real-time Status**: See current YOLO detection status
- **Easy Toggle**: Enable/disable detection with one click
- **Configuration**: Adjust confidence threshold and model selection
- **Quick Access**: Direct links to video feed and other parts of the system

### Status Indicators:
- 🟢 **Green**: Feature enabled and working
- 🔴 **Red**: Feature disabled
- 🟡 **Yellow**: Warning (dependencies missing, model not loaded, etc.)

## 🔧 API Endpoints

### Get Status
```bash
GET /Sensory_Memory/yolo_status/
```

Response:
```json
{
  "status": "success",
  "yolo_enabled": true,
  "dependencies_available": true,
  "detector_working": true,
  "config": {
    "model_path": "yolov8n.pt",
    "confidence_threshold": 0.5,
    "detection_interval": 1
  }
}
```

### Toggle Detection
```bash
POST /Sensory_Memory/toggle_yolo/
```

### Update Configuration
```bash
POST /Sensory_Memory/yolo_config/
Content-Type: application/json

{
  "confidence_threshold": 0.7,
  "model_path": "yolov8s.pt"
}
```

## 📁 File Structure

```
LouBot-AI/
├── Sensory_Memory/
│   ├── yolo_detector.py          # YOLOv8 detection logic
│   ├── detection_config.py       # Configuration settings
│   └── views.py                  # Updated with YOLO integration
├── templates/
│   └── yolo_management.html      # Web management interface
├── requirements.txt              # Updated with ultralytics
└── YOLO_INTEGRATION_README.md    # This file
```

## 🛠️ Configuration Details

### Performance Settings

```python
# In detection_config.py

# Process every N frames (1 = every frame, 2 = every other frame)
DETECTION_INTERVAL = 1

# Bounding box appearance
BBOX_COLOR = (0, 255, 0)     # Green
BBOX_THICKNESS = 2
TEXT_COLOR = (0, 0, 0)       # Black text
TEXT_SCALE = 0.6
```

### Memory Usage
- **YOLOv8n**: ~200MB RAM
- **YOLOv8s**: ~400MB RAM  
- **YOLOv8m**: ~800MB RAM
- **YOLOv8l**: ~1.5GB RAM
- **YOLOv8x**: ~2.5GB RAM

## 🔥 Easy Removal Guide

If you want to remove YOLO integration completely:

### Option 1: Disable Only
```python
# In Sensory_Memory/detection_config.py
ENABLE_YOLO_DETECTION = False
```

### Option 2: Complete Removal
1. **Remove files:**
   ```bash
   rm Sensory_Memory/yolo_detector.py
   rm Sensory_Memory/detection_config.py
   rm templates/yolo_management.html
   ```

2. **Remove from URLs:**
   ```python
   # In Sensory_Memory/urls.py - remove YOLO URL patterns
   ```

3. **Remove from views:**
   ```python
   # In Sensory_Memory/views.py - remove YOLO management functions
   ```

4. **Revert video generation:**
   Replace the modified `generate_video_frames()` with the original version.

5. **Remove dependencies:**
   ```bash
   pip uninstall ultralytics
   # Remove ultralytics from requirements.txt
   ```

## 📊 Detected Objects

YOLOv8 can detect 80 different object classes including:

**People & Animals**: person, cat, dog, bird, horse, sheep, cow, elephant, bear, zebra, giraffe

**Vehicles**: car, motorcycle, airplane, bus, train, truck, boat, bicycle

**Indoor Objects**: chair, couch, bed, dining table, toilet, tv, laptop, mouse, keyboard, cell phone

**And many more!**

## 🐛 Troubleshooting

### Common Issues

1. **"ultralytics package not installed"**
   ```bash
   pip install ultralytics==8.2.31
   ```

2. **Model download fails**
   - Check internet connection
   - Model will auto-download on first use

3. **High CPU/Memory usage**
   - Use smaller model (yolov8n.pt)
   - Increase `DETECTION_INTERVAL` to process fewer frames

4. **No detections showing**
   - Check confidence threshold (lower = more detections)
   - Ensure good lighting for drone camera
   - Objects must be clearly visible

### Performance Tips

- **For real-time detection**: Use `yolov8n.pt` with `DETECTION_INTERVAL = 1`
- **For accuracy**: Use `yolov8m.pt` or larger with `DETECTION_INTERVAL = 2-3`
- **For low-end hardware**: Use `yolov8n.pt` with `DETECTION_INTERVAL = 3-5`

## 🚀 Advanced Usage

### Custom Object Detection

You can train custom YOLOv8 models and use them:

```python
# In detection_config.py
YOLO_MODEL_PATH = 'path/to/your/custom_model.pt'
```

### Integration with LouBot AI

The detection results can be integrated with the AI chat system:

```python
# Example: Get detections programmatically
from Sensory_Memory.yolo_detector import get_yolo_detector

detector = get_yolo_detector()
detections = detector.detect_objects(frame)
# detections = [{'class_name': 'person', 'confidence': 0.85, ...}, ...]
```

## 📞 Support

- **Configuration Issues**: Check `detection_config.py` settings
- **Performance Issues**: Adjust model size and detection interval
- **Integration Issues**: Ensure all files are in correct locations

---

**Happy Object Detection! 🎯**

The integration is designed to enhance your LouBot experience while maintaining the flexibility to disable or remove it whenever needed. 