"""
YOLOv8 Object Detection Module for Drone Video Feed
==================================================

This module provides YOLOv8 object detection capabilities that can be 
seamlessly integrated with the drone video streaming system.

Features:
- Easy to enable/disable
- Configurable confidence threshold
- Draws bounding boxes and class names
- Can be easily removed without affecting core functionality

Usage:
    from .yolo_detector import YOLODetector
    
    detector = YOLODetector()
    processed_frame = detector.detect_and_draw(frame)
"""

import cv2
import logging
from ultralytics import YOLO
import numpy as np
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YOLODetector:
    """
    YOLOv8 Object Detection wrapper for drone video processing.
    """
    
    def __init__(self, model_path='yolov8n.pt', confidence_threshold=0.5):
        """
        Initialize YOLOv8 detector.
        
        Args:
            model_path (str): Path to YOLOv8 model file
            confidence_threshold (float): Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.class_names = []
        
        try:
            logger.info(f"Loading YOLOv8 model: {model_path}")
            
            # Handle PyTorch 2.6+ security restrictions for YOLO models
            # Temporarily patch torch.load to use weights_only=False for ultralytics
            import os
            os.environ['YOLO_WEIGHTS_ONLY'] = 'False'
            
            # Try to load with explicit weights_only=False if supported
            try:
                # For ultralytics models, we need to allow pickle loading
                import ultralytics.nn.tasks
                torch.serialization.add_safe_globals([
                    ultralytics.nn.tasks.DetectionModel,
                    ultralytics.nn.tasks.ClassificationModel,
                    ultralytics.nn.tasks.SegmentationModel,
                    ultralytics.nn.tasks.PoseModel
                ])
                self.model = YOLO(model_path)
            except Exception as safe_error:
                logger.warning(f"Safe loading failed, trying alternative method: {safe_error}")
                # Alternative: monkey patch torch.load temporarily
                original_load = torch.load
                def patched_load(*args, **kwargs):
                    kwargs['weights_only'] = False
                    return original_load(*args, **kwargs)
                
                torch.load = patched_load
                try:
                    self.model = YOLO(model_path)
                    logger.info("Successfully loaded YOLO model with patched torch.load")
                finally:
                    # Restore original torch.load
                    torch.load = original_load
            
            # Get class names from the model
            if hasattr(self.model, 'names'):
                self.class_names = list(self.model.names.values())
            else:
                # Default COCO class names if not available from model
                self.class_names = [
                    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
                    'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
                    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
                    'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
                    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
                    'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
                    'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
                    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
                    'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
                    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
                    'toothbrush'
                ]
            
            logger.info(f"YOLOv8 model loaded successfully with {len(self.class_names)} classes")
            
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            self.model = None
    
    def is_available(self):
        """Check if YOLO model is loaded and available."""
        return self.model is not None
    
    def detect_and_draw(self, frame):
        """
        Perform object detection on frame and draw bounding boxes.
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            Processed frame with bounding boxes and labels
        """
        if not self.is_available():
            return frame
            
        try:
            # Run YOLOv8 inference
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            
            # Process results
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        
                        # Get class name
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"Class_{class_id}"
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Draw label with background
                        label = f"{class_name}: {confidence:.2f}"
                        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                        
                        # Background rectangle for text
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), (0, 255, 0), -1)
                        
                        # Text
                        cv2.putText(frame, label, (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error during YOLO detection: {e}")
            return frame
    
    def detect_objects(self, frame):
        """
        Perform object detection and return detection results without drawing.
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            List of detection dictionaries with keys: 'bbox', 'confidence', 'class_name', 'class_id'
        """
        detections = []
        
        if not self.is_available():
            return detections
            
        try:
            # Run YOLOv8 inference
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            
            # Process results
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        
                        # Get class name
                        class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"Class_{class_id}"
                        
                        detections.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': confidence,
                            'class_name': class_name,
                            'class_id': class_id
                        })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during YOLO detection: {e}")
            return detections


# Global detector instance (singleton pattern)
_detector_instance = None

def get_yolo_detector(model_path='yolov8n.pt', confidence_threshold=0.5):
    """
    Get or create a global YOLO detector instance.
    
    Args:
        model_path (str): Path to YOLOv8 model file
        confidence_threshold (float): Minimum confidence for detections
        
    Returns:
        YOLODetector instance
    """
    global _detector_instance
    
    if _detector_instance is None:
        _detector_instance = YOLODetector(model_path, confidence_threshold)
    
    return _detector_instance

def reset_yolo_detector():
    """Reset the global detector instance (useful for testing or reloading)."""
    global _detector_instance
    _detector_instance = None 