"""
Detection Bridge System
======================

This module provides a bridge between YOLO object detection and AIML chat queries.
It stores current detections in a format that AIML can quickly access for real-time responses.

The system maintains a temporary store of the most recent detections for each session,
allowing the chatbot to answer questions like "what can you see?" and "do you see a person?".
"""

import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Global storage for current detections
# Structure: {session_id: {'detections': [...], 'timestamp': datetime, 'lock': threading.Lock()}}
_detection_store = {}
_store_lock = threading.Lock()

# Detection expiry time (detections older than this are considered stale)
DETECTION_EXPIRY_SECONDS = 10

class DetectionStore:
    """Manages real-time detection storage for AIML integration."""
    
    @staticmethod
    def update_detections(session_id: str, detections: List[Dict]) -> None:
        """
        Update the current detections for a session.
        
        Args:
            session_id: User session identifier
            detections: List of detection dicts with keys: name, confidence, bbox
        """
        with _store_lock:
            if session_id not in _detection_store:
                _detection_store[session_id] = {
                    'detections': [],
                    'timestamp': datetime.now(),
                    'lock': threading.Lock()
                }
            
            session_data = _detection_store[session_id]
            with session_data['lock']:
                session_data['detections'] = detections
                session_data['timestamp'] = datetime.now()
    
    @staticmethod
    def get_current_detections(session_id: str = None) -> List[Dict]:
        """
        Get current detections for a session.
        
        Args:
            session_id: User session identifier (if None, returns empty list)
            
        Returns:
            List of current detection objects with name, confidence, bbox
        """
        if not session_id:
            return []
            
        with _store_lock:
            if session_id not in _detection_store:
                return []
            
            session_data = _detection_store[session_id]
            
        with session_data['lock']:
            # Check if detections are still fresh
            time_diff = datetime.now() - session_data['timestamp']
            if time_diff.total_seconds() > DETECTION_EXPIRY_SECONDS:
                return []  # Stale detections
            
            return session_data['detections'].copy()
    
    @staticmethod
    def find_object(session_id: str, object_name: str) -> Optional[Dict]:
        """
        Find a specific object in current detections.
        
        Args:
            session_id: User session identifier
            object_name: Name of object to find (case insensitive)
            
        Returns:
            Detection dict if found, None otherwise
        """
        detections = DetectionStore.get_current_detections(session_id)
        object_name_lower = object_name.lower()
        
        for detection in detections:
            if object_name_lower in detection['name'].lower():
                return detection
        return None
    
    @staticmethod
    def count_objects(session_id: str, object_name: str = None) -> int:
        """
        Count objects in current detections.
        
        Args:
            session_id: User session identifier
            object_name: Specific object to count (if None, counts all objects)
            
        Returns:
            Number of matching objects
        """
        detections = DetectionStore.get_current_detections(session_id)
        
        if not object_name:
            return len(detections)
        
        object_name_lower = object_name.lower()
        count = 0
        for detection in detections:
            if object_name_lower in detection['name'].lower():
                count += 1
        return count
    
    @staticmethod
    def get_detection_summary(session_id: str) -> str:
        """
        Get a human-readable summary of current detections.
        
        Args:
            session_id: User session identifier
            
        Returns:
            Formatted string describing current detections
        """
        detections = DetectionStore.get_current_detections(session_id)
        
        if not detections:
            return "No objects detected in current field of view"
        
        # Group objects by name
        object_counts = {}
        for detection in detections:
            name = detection['name']
            object_counts[name] = object_counts.get(name, 0) + 1
        
        # Format summary
        summary_parts = []
        for obj_name, count in object_counts.items():
            if count == 1:
                summary_parts.append(f"1 {obj_name}")
            else:
                summary_parts.append(f"{count} {obj_name}s")
        
        return f"Currently seeing: {', '.join(summary_parts)}"
    
    @staticmethod
    def cleanup_old_sessions() -> None:
        """Remove detection data for sessions that haven't been updated recently."""
        with _store_lock:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session_data in _detection_store.items():
                time_diff = current_time - session_data['timestamp']
                if time_diff.total_seconds() > 300:  # 5 minutes
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del _detection_store[session_id]

    @staticmethod
    def get_detection_stats() -> Dict:
        """Get statistics about the detection store."""
        with _store_lock:
            active_sessions = len(_detection_store)
            total_detections = sum(
                len(data['detections']) 
                for data in _detection_store.values()
            )
            return {
                'active_sessions': active_sessions,
                'total_detections': total_detections,
                'store_size': len(_detection_store)
            }

# Convenience functions for AIML integration
def update_detections(session_id: str, detections: List[Dict]) -> None:
    """Update detections for a session (convenience function)."""
    DetectionStore.update_detections(session_id, detections)

def get_current_detections(session_id: str = None) -> List[Dict]:
    """Get current detections for a session (convenience function)."""
    return DetectionStore.get_current_detections(session_id)

def find_object(session_id: str, object_name: str) -> Optional[Dict]:
    """Find specific object in current detections (convenience function)."""
    return DetectionStore.find_object(session_id, object_name)

def count_objects(session_id: str, object_name: str = None) -> int:
    """Count objects in current detections (convenience function)."""
    return DetectionStore.count_objects(session_id, object_name)

# Auto-cleanup thread
def _start_cleanup_thread():
    """Start background thread for cleanup."""
    def cleanup_worker():
        while True:
            time.sleep(60)  # Run every minute
            DetectionStore.cleanup_old_sessions()
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

# Start cleanup when module is imported
_start_cleanup_thread() 