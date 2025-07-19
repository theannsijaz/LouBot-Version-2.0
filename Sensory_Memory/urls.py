from django.urls import path
from . import views

urlpatterns = [
    path('drone_video_feed/',views.drone_video_feed, name='drone_video_feed'),
    path('take_picture/',views.take_picture, name='take_picture'),
    
    # Drone Connection Management Endpoints
    path('reset_drone_connection/',views.reset_drone_connection, name='reset_drone_connection'),
    path('drone_status/',views.drone_status, name='drone_status'),
    
    # YOLO Detection Management Endpoints
    path('yolo_status/',views.yolo_status, name='yolo_status'),
    path('toggle_yolo/',views.toggle_yolo, name='toggle_yolo'),
    path('yolo_config/',views.yolo_config, name='yolo_config'),
    path('yolo_management/',views.yolo_management_page, name='yolo_management_page'),
    path('current_detections/',views.current_detections_text, name='current_detections'),
]