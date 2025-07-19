"""
Detection Configuration Module
=============================

This module provides easy configuration for object detection features.
Change these settings to enable/disable and configure detection behavior.

To enable YOLO detection:
    - Set ENABLE_YOLO_DETECTION = True
    - Ensure YOLOv8 model is available
    - Install ultralytics package

To disable:
    - Set ENABLE_YOLO_DETECTION = False
    - No YOLO dependencies needed
"""

# =============================================================================
# MAIN CONFIGURATION SWITCHES
# =============================================================================

# Enable/Disable YOLO Object Detection
# Set to False to completely disable YOLO processing
ENABLE_YOLO_DETECTION = True

# =============================================================================
# YOLO DETECTION SETTINGS
# =============================================================================

# YOLOv8 Model Configuration
YOLO_MODEL_PATH = '/Users/annsijaz/Downloads/yolov8m.pt'  # Can be 'yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt'
YOLO_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for detections (0.0 - 1.0)

# Detection Display Settings
BBOX_COLOR = (0, 255, 0)  # Green bounding box color (BGR format)
BBOX_THICKNESS = 2        # Bounding box line thickness
TEXT_COLOR = (0, 0, 0)    # Black text color (BGR format)
TEXT_SCALE = 0.6          # Text size scale
TEXT_THICKNESS = 2        # Text thickness

# Performance Settings
DETECTION_INTERVAL = 1    # Process every N frames (1 = every frame, 2 = every other frame, etc.)

# =============================================================================
# SAFETY CHECKS AND HELPERS
# =============================================================================

def is_yolo_enabled():
    """Check if YOLO detection is enabled."""
    return ENABLE_YOLO_DETECTION

def get_yolo_config():
    """Get YOLO configuration as a dictionary."""
    return {
        'enabled': ENABLE_YOLO_DETECTION,
        'model_path': YOLO_MODEL_PATH,
        'confidence_threshold': YOLO_CONFIDENCE_THRESHOLD,
        'bbox_color': BBOX_COLOR,
        'bbox_thickness': BBOX_THICKNESS,
        'text_color': TEXT_COLOR,
        'text_scale': TEXT_SCALE,
        'text_thickness': TEXT_THICKNESS,
        'detection_interval': DETECTION_INTERVAL
    }

def check_yolo_dependencies():
    """
    Check if YOLO dependencies are available.
    Returns (bool, str): (is_available, message)
    """
    if not ENABLE_YOLO_DETECTION:
        return True, "YOLO detection is disabled"
    
    try:
        import ultralytics
        return True, "YOLO dependencies available"
    except ImportError:
        return False, "ultralytics package not installed. Run: pip install ultralytics"

# =============================================================================
# EASY TOGGLE FUNCTIONS
# =============================================================================

def enable_yolo():
    """Enable YOLO detection (requires restart to take effect)."""
    global ENABLE_YOLO_DETECTION
    ENABLE_YOLO_DETECTION = True
    print("YOLO detection enabled. Restart the server to apply changes.")

def disable_yolo():
    """Disable YOLO detection (requires restart to take effect)."""
    global ENABLE_YOLO_DETECTION
    ENABLE_YOLO_DETECTION = False
    print("YOLO detection disabled. Restart the server to apply changes.")

def set_confidence_threshold(threshold):
    """Set YOLO confidence threshold (0.0 - 1.0)."""
    global YOLO_CONFIDENCE_THRESHOLD
    if 0.0 <= threshold <= 1.0:
        YOLO_CONFIDENCE_THRESHOLD = threshold
        print(f"YOLO confidence threshold set to {threshold}")
    else:
        print("Confidence threshold must be between 0.0 and 1.0")

def set_model_path(model_path):
    """Set YOLOv8 model path."""
    global YOLO_MODEL_PATH
    YOLO_MODEL_PATH = model_path
    print(f"YOLO model path set to {model_path}")

# =============================================================================
# INFORMATION DISPLAY
# =============================================================================

def print_current_config():
    """Print current detection configuration."""
    config = get_yolo_config()
    print("\n" + "="*50)
    print("CURRENT DETECTION CONFIGURATION")
    print("="*50)
    
    for key, value in config.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    available, message = check_yolo_dependencies()
    print(f"Dependencies: {message}")
    print("="*50 + "\n")

# Print configuration on import (for debugging)
if __name__ == "__main__":
    print_current_config() 