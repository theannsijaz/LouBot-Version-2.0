from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import StreamingHttpResponse
from datetime import datetime, timedelta
from djitellopy import Tello
from Memory.models import *
import cv2
import os
import time
import base64
import logging
from django.http import JsonResponse
from django.conf import settings


is_recording = False
out = None

# Track whether video stream was already started to avoid repeated
# streamon/streamoff cycles which can break the decoder.
stream_started = False

# ------------------------------------------------------------------
# Re-use a single Tello connection instead of creating a new one each
# time.  Prevents the OSError: [Errno 48] Address already in use and
# lets us query battery once and share the link.
# ------------------------------------------------------------------

tello_singleton = None
is_flying = False        # <- add this line


def get_tello():
    """Return a connected Tello instance (singleton)."""
    global tello_singleton
    if tello_singleton is None:
        tello_singleton = Tello()
        tello_singleton.connect()
        # Ensure SDK mode is active
        try:
            tello_singleton.send_command_without_return("command")
            time.sleep(0.5)
        except:
            pass
        print(f"[TELLO] Battery level: {tello_singleton.get_battery()}%")
    return tello_singleton

def reset_tello_connection():
    """Reset the Tello connection if it gets into a bad state."""
    global tello_singleton, stream_started
    if tello_singleton is not None:
        try:
            tello_singleton.streamoff()
        except:
            pass
        try:
            tello_singleton.end()
        except:
            pass
        tello_singleton = None
        stream_started = False
    
    # Create new connection
    tello_singleton = Tello()
    tello_singleton.connect()
    
    # Ensure we're in SDK mode
    try:
        tello_singleton.send_command_without_return("command")
        time.sleep(0.5)
        print("[TELLO] Connection reset and SDK mode activated")
    except Exception as e:
        print(f"[TELLO] Error setting SDK mode: {e}")
    
    return tello_singleton


def get_current_wifi_name():
    if sys.platform.startswith("darwin"):  # macOS
        try:
            result = subprocess.run(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if " SSID:" in line:
                    return line.split(":")[1].strip()
        except Exception as e:
            print(f"[macOS] Error fetching WiFi SSID: {e}")
            return None
    else:  # Windows or Linux (pywifi works)
        try:
            import pywifi
            from pywifi import PyWiFi, const

            wifi = PyWiFi()
            iface = wifi.interfaces()[0]
            iface.scan()
            profiles = iface.network_profiles()
            if profiles:
                return profiles[0].ssid
        except Exception as e:
            print(f"[Non-macOS] Error fetching WiFi SSID: {e}")
            return None


logging.basicConfig(level=logging.INFO)


def Tello_Takeoff():
    refresh_flying_flag()
    global is_flying          #  ←  restore this
    tel = get_tello()
    if tel.get_battery() < 15:
        print("[TELLO] Battery too low for take-off.")
        return "Battery too low to fly. Please charge the drone before takeoff."
    if is_flying:
        print("[TELLO] Already airborne; ignoring takeoff.")
        return "Drone is already airborne."
    try:
        # Ensure SDK mode before takeoff
        tel.send_command_without_return("command")
        time.sleep(0.5)
        tel.takeoff()
        is_flying = True
        return "Takeoff successful! Drone is now airborne."
    except OSError as e:
        print("[TELLO] OS error during takeoff:", e)
        return f"Error during takeoff: {str(e)}"
    except Exception as e:
        print("Error taking off:", e)
        # Try connection reset if takeoff fails
        if "error" in str(e).lower():
            try:
                print("[TELLO] Attempting connection reset and retry...")
                reset_tello_connection()
                time.sleep(1)
                tel = get_tello()
                tel.takeoff()
                is_flying = True
                return "Takeoff successful after connection reset! Drone is now airborne."
            except Exception as retry_error:
                return f"Failed to takeoff even after connection reset: {str(retry_error)}"
        return f"Failed to takeoff: {str(e)}"

def Tello_Land():
    refresh_flying_flag()        # ← restore this
    global is_flying
    tel = get_tello()
    try:
        tel.land()
        is_flying = False
        return "Landing successful! Drone has landed safely."
    except Exception as e:
        print("Error landing:", e)
        return f"Error during landing: {str(e)}"


def warmup(seconds=3):
    refresh_flying_flag()
    global is_flying
    tel = get_tello()
    if tel.get_battery() < 15:
        print("[TELLO] Battery too low for warm-up.")
        return "Battery too low to fly."
    if is_flying:
        print("[TELLO] Already airborne; skipping warm-up")
        return "Already airborne; skipping warm-up"
    tel.takeoff()
    is_flying = True
    time.sleep(int(seconds))
    tel.land()
    is_flying = False
    return "Warm-up completed successfully"




def fetch_drone_data():
    """Return a dict of the most recent telemetry from the drone."""
    tello = get_tello()
    def query_temperature(tello):
        response = tello.send_read_command('temp?')
        return response

    def query_barometer(tello):
        response = tello.send_read_command('baro?')
        return response

    def query_attitude(tello):
        response = tello.send_read_command('attitude?')
        return response

    def query_speed(tello):
        response = tello.send_read_command('speed?')
        return response

    def query_height(tello):
        response = tello.send_read_command('height?')
        return response

    def query_flight_time(tello):
        response = tello.get_flight_time()
        return response

    def query_distance_tof(tello):
        response = tello.get_distance_tof()
        return response

    temperature_range = query_temperature(tello)
    battery = tello.query_battery()
    barometer = query_barometer(tello)
    attitude = query_attitude(tello)
    speed = query_speed(tello)
    height = query_height(tello)
    flight_time = query_flight_time(tello)
    distance_tof = query_distance_tof(tello)

    temperatures = temperature_range.replace('C', '').split('~')
    lowest_temp = min(int(temperatures[0]), int(temperatures[1]))
    highest_temp = max(int(temperatures[0]), int(temperatures[1]))

    return {'temperature_range': temperature_range,'lowest_temperature': lowest_temp,'highest_temperature': highest_temp,'battery': battery,
            'barometer': barometer,'attitude': attitude,'speed': speed,'height': height,'flight_time':flight_time,'distance_tof': distance_tof}


















# def generate_video_frames():
#     tello = Tello()
#     tello.connect()
#     tello.streamon()
    
#     try:
#         while True:
#             frame = tello.get_frame_read().frame
#             _, jpeg = cv2.imencode('.jpg', frame)
#             yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
#     except KeyboardInterrupt:
#         tello.streamoff()
#         tello.land()
#         tello.end()
#         exit(1)


# def drone_video_feed(request):
#     return StreamingHttpResponse(generate_video_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


def generate_video_frames(session_id='default'):
    global stream_started
    tello = get_tello()
    
    # Import YOLO components conditionally
    yolo_detector = None
    frame_counter = 0
    
    # Import detection bridge for storing detections
    try:
        from Memory.detection_bridge import update_detections
        detection_bridge_available = True
    except ImportError:
        detection_bridge_available = False
        logging.warning("Detection bridge not available")
    
    # Try to initialize YOLO if enabled
    try:
        from .detection_config import is_yolo_enabled, get_yolo_config
        from .yolo_detector import get_yolo_detector
        
        if is_yolo_enabled():
            config = get_yolo_config()
            yolo_detector = get_yolo_detector(
                model_path=config['model_path'],
                confidence_threshold=config['confidence_threshold']
            )
            if yolo_detector.is_available():
                logging.info("YOLO detection enabled for video stream")
            else:
                logging.warning("YOLO detector not available, continuing without detection")
                yolo_detector = None
        else:
            logging.info("YOLO detection disabled")
    except ImportError as e:
        logging.warning(f"YOLO dependencies not available: {e}")
        yolo_detector = None
    except Exception as e:
        logging.error(f"Error initializing YOLO detector: {e}")
        yolo_detector = None
    
    # Start stream only once
    if not stream_started:
        try:
            tello.streamon()
            stream_started = True
        except Exception as e:
            logging.error(f"Error starting video stream: {e}")

    try:
        while True:
            frame_read = tello.get_frame_read()
            if frame_read.stopped:
                logging.error("Frame reader stopped; breaking video loop")
                break
            
            frame = frame_read.frame
            if frame is not None:
                # Apply YOLO detection if available and enabled
                if yolo_detector is not None:
                    try:
                        # Process every frame or at intervals based on config
                        config = get_yolo_config()
                        if frame_counter % config.get('detection_interval', 1) == 0:
                            # Get detections first
                            detections = yolo_detector.detect_objects(frame)
                            
                            # Store detections in bridge for AIML access
                            if detection_bridge_available and detections:
                                # Format detections for the bridge
                                formatted_detections = []
                                for detection in detections:
                                    formatted_detections.append({
                                        'name': detection['class_name'],
                                        'confidence': detection['confidence'], 
                                        'bbox': detection['bbox']
                                    })
                                
                                # Update detection store with actual session ID
                                update_detections(session_id, formatted_detections)
                            
                            # Draw detections on frame
                            frame = yolo_detector.detect_and_draw(frame)
                    except Exception as e:
                        logging.error(f"Error during YOLO processing: {e}")
                        # Continue with original frame if YOLO fails
                
                frame_counter += 1
                
                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            else:
                logging.error("Frame is None")
                continue
            
            time.sleep(0.1)  # Sleep to prevent high CPU usage
    except Exception as e:
        logging.error(f"Error during video stream handling: {e}")

def create_parts(text_node,session,parts):
    part_u = CommandPart(part=parts).save()
    text_node.text_part.connect(part_u)

def get_command(message,session):
    if message and session:
        text_node = CommandText(sentence=message).save()

        # Ensure a TextSensor node exists for this session
        try:
            n = TextSensor.nodes.filter(uid=session).first()
        except TextSensor.DoesNotExist:
            n = None

        if not n:
            # Create the missing TextSensor
            n = TextSensor(uid=session, name="Text Sensor").save()
            # Also ensure a Sensor container exists and link it
            try:
                sensor_container = SensoryMemory.nodes.filter(uid=session).first()
            except SensoryMemory.DoesNotExist:
                sensor_container = None
            
            if not sensor_container:
                sensor_container = SensoryMemory(uid=session, name="Sensor").save()
            sensor_container.textsense.connect(n)

        # Connect current command text to the TextSensor
        n.text_sense.connect(text_node)

        for part in message.split():
            create_parts(text_node, session, part)

def make_sensory_and_link(request):
    session = request.session.get('user_id')
    user = Signups.nodes.filter(uid=session).first()
    try:
        sensor_node = SensoryMemory.nodes.get(uid = session,name='Sensor')
    except:
        sensor_node = SensoryMemory(uid = session,name='Sensor').save()
        user.sense.connect(sensor_node)

    try:
        text_node = TextSensor.nodes.get(uid = session,name='Text Sensor')
    except:
        text_node = TextSensor(uid = session,name='Text Sensor').save()
        sensor_node.textsense.connect(text_node)

    try:
        agent = Sensor.nodes.get(uid = session,name='DJI-TELLO')
    except:
        agent = Sensor(uid = session,name='DJI-TELLO').save()
        sensor_node.sensor.connect(agent)


def update_sensor(request):
    session = request.session.get('user_id')    
    drone_data = fetch_drone_data()
    agent = Sensor.nodes.get(uid = session,name='DJI-TELLO')
    existing_flights_count=""
    try:
        existing_flights_count = Sense.nodes.filter(sense_name__startswith="FLIGHT").count()
    except:
        existing_flights_count = 0

    flight_number = existing_flights_count + 1

    sensor_node = ""
    try:   
        sensor_node = Sense.nodes.filter(created_at__gte=datetime.now() - timedelta(minutes=15)).order_by('-created_at').first()
        sensor_node.updated_on = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sensor_node.save()
    except:
        sensor_node = Sense()
        

    sensor_node.sense_name = f"FLIGHT {flight_number}"
    sensor_node.temperature_range = f"{drone_data['temperature_range']}°C"
    sensor_node.lowest_temperature = f"{drone_data['lowest_temperature']}°C"
    sensor_node.highest_temperature = f"{drone_data['highest_temperature']}°C"
    sensor_node.battery = f"{drone_data['battery']}%"
    sensor_node.barometer = f"{drone_data['barometer']} mbar"
    sensor_node.attitude = f"{drone_data['attitude']}"
    sensor_node.speed = f"{drone_data['speed']} cm/s"
    sensor_node.height = f"{drone_data['height']}"
    sensor_node.flight_time = f"{drone_data['flight_time']} seconds"
    sensor_node.distance_tof = f"{drone_data['distance_tof']} cm" 
    sensor_node.save()

    agent.sense.connect(sensor_node)

        



# def generate_video_frames(request):
#     check_for = get_current_wifi_name()
#     if check_for:
#         from Memory.views import make_sensory_and_link
#         make_sensory_and_link(request)
#         update_sensor(request)
#         tello = Tello()
#         tello.connect()
#         tello.streamon()

#         try:
#             while True:
#                 frame_read = tello.get_frame_read()
#                 if frame_read.stopped:
#                     tello.streamoff()
#                     tello.end()
#                     break
                
#                 frame = frame_read.frame
#                 if frame is not None:
#                     classIds, confs, bbox = net.detect(frame, confThreshold=thres, nmsThreshold=nmsThres)
#                     try:
#                         for classId, conf, box in zip(classIds.flatten(), confs.flatten(), bbox):
#                             cvzone.cornerRect(frame, box)
#                             cv2.putText(frame, f'{classNames[classId - 1].upper()} {round(conf * 100, 2)}',
#                                         (box[0] + 10, box[1] + 30), cv2.FONT_HERSHEY_COMPLEX_SMALL,
#                                         1, (0, 255, 0), 2)
#                     except Exception as e:
#                         logging.error(f"Error during object detection: {e}")

#                     _, jpeg = cv2.imencode('.jpg', frame)
#                     yield (b'--frame\r\n'
#                            b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
#                 else:
#                     logging.error("Frame is None")
#                     continue
                
#                 time.sleep(0.1)  
#         except Exception as e:
#             logging.error(f"Error during video stream handling: {e}")
#         finally:
#             tello.streamoff()
#             tello.end()


import sys
import logging
import time
import subprocess
from django.http import StreamingHttpResponse

# -------------------------------------------------------------
# Non-blocking command helpers
# -------------------------------------------------------------

import threading

# We allow only one SDK command at a time – Tello rejects parallel commands.
command_lock = threading.Lock()


def _run_in_thread(fn, *args, **kwargs):
    """Utility: run *fn* in a daemon thread so the caller returns instantly."""

    def _target():
        with command_lock:
            try:
                fn(*args, **kwargs)
            except Exception as e:
                print("[TELLO] Command error:", e)

    threading.Thread(target=_target, daemon=True).start()


@require_GET
def drone_video_feed(request):
    # Get session ID for detection bridge
    session_id = request.session.get('user_id', 'default')
    return StreamingHttpResponse(
        generate_video_frames(session_id), 
        content_type='multipart/x-mixed-replace; boundary=frame'
    )










def take_picture(request):
    global stream_started
    tel = get_tello()
    try:
        if not stream_started:
            tel.streamon()
            stream_started = True

        # Capture frame from the video stream
        frame_read = tel.get_frame_read()
        frame = frame_read.frame

        if frame is not None:
            # Save image to 'static' folder (ensure 'static' folder exists in your project)
            file_path = os.path.join(settings.BASE_DIR, 'static', 'tello_picture.jpg')
            cv2.imwrite(file_path, frame)

            # Convert image to base64 (optional)
            with open(file_path, 'rb') as img_file:
                img_str = base64.b64encode(img_file.read()).decode('utf-8')

            return JsonResponse({'status': 'success', 'image': img_str})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to capture frame from drone'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    finally:
        # keep stream running for other consumers; do not streamoff/end
        pass

        
def _execute_movement_with_retry(movement_func, distance, direction_name):
    """Execute movement command with automatic retry on 'Not joystick' error."""
    try:
        movement_func(int(distance))
        return f"Moving {direction_name} {distance} cm"
    except Exception as e:
        error_msg = str(e)
        if "Not joystick" in error_msg or "error" in error_msg.lower():
            print(f"[TELLO] Movement error detected: {error_msg}. Resetting connection...")
            try:
                # Reset connection and try again
                reset_tello_connection()
                time.sleep(1)  # Give time for connection to stabilize
                tel = get_tello()
                # Re-get the movement function from the new connection
                func_name = movement_func.__name__
                new_movement_func = getattr(tel, func_name)
                new_movement_func(int(distance))
                return f"Connection reset. Moving {direction_name} {distance} cm"
            except Exception as retry_error:
                return f"Movement failed even after connection reset: {str(retry_error)}"
        else:
            return f"Movement error: {error_msg}"

def Move_Forward(x):
    tel = get_tello()
    if tel.get_battery() < 5:
        return "Battery too low for movement commands. Please charge the drone."
    return _execute_movement_with_retry(tel.move_forward, x, "forward")

def Move_Backward(x):
    tel = get_tello()
    if tel.get_battery() < 5:
        return "Battery too low for movement commands. Please charge the drone."
    return _execute_movement_with_retry(tel.move_back, x, "backward")

def Move_Left(x):
    tel = get_tello()
    if tel.get_battery() < 5:
        return "Battery too low for movement commands. Please charge the drone."
    return _execute_movement_with_retry(tel.move_left, x, "left")

def Move_Right(x):
    tel = get_tello()
    if tel.get_battery() < 5:
        return "Battery too low for movement commands. Please charge the drone."
    return _execute_movement_with_retry(tel.move_right, x, "right")

# Optionally run take-off / land asynchronously too so chat doesn’t block.

def async_takeoff():
    _run_in_thread(lambda: Tello_Takeoff())

def async_land():
    _run_in_thread(lambda: Tello_Land())

def refresh_flying_flag():
    """
    Update is_flying based on the drone's reported height.
    """
    global is_flying
    try:
        tel = get_tello()
        current_height = tel.get_height()       # height in cm
        is_flying = current_height > 10         # treat >10 cm as airborne
    except Exception as e:
        print("[TELLO] Could not read height:", e)


# =============================================================================
# YOLO Detection Management Endpoints
# =============================================================================

def yolo_status(request):
    """Get current YOLO detection status and configuration."""
    try:
        from .detection_config import is_yolo_enabled, get_yolo_config, check_yolo_dependencies
        
        config = get_yolo_config()
        dependencies_available, dep_message = check_yolo_dependencies()
        
        # Try to check if detector is actually working
        detector_working = False
        if config['enabled'] and dependencies_available:
            try:
                from .yolo_detector import get_yolo_detector
                detector = get_yolo_detector()
                detector_working = detector.is_available()
            except Exception as e:
                detector_working = False
        
        return JsonResponse({
            'status': 'success',
            'yolo_enabled': config['enabled'],
            'dependencies_available': dependencies_available,
            'dependency_message': dep_message,
            'detector_working': detector_working,
            'config': config
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Error getting YOLO status: {str(e)}"
        })

def toggle_yolo(request):
    """Toggle YOLO detection on/off."""
    try:
        from .detection_config import is_yolo_enabled, enable_yolo, disable_yolo
        
        current_status = is_yolo_enabled()
        
        if current_status:
            disable_yolo()
            new_status = False
            message = "YOLO detection disabled. Restart server to apply changes."
        else:
            enable_yolo()
            new_status = True
            message = "YOLO detection enabled. Restart server to apply changes."
        
        return JsonResponse({
            'status': 'success',
            'yolo_enabled': new_status,
            'message': message,
            'restart_required': True
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Error toggling YOLO: {str(e)}"
        })

def yolo_config(request):
    """Get or update YOLO configuration."""
    try:
        from .detection_config import get_yolo_config, set_confidence_threshold, set_model_path
        
        if request.method == 'GET':
            config = get_yolo_config()
            return JsonResponse({
                'status': 'success',
                'config': config
            })
            
        elif request.method == 'POST':
            import json
            data = json.loads(request.body)
            
            updated_settings = []
            
            # Update confidence threshold if provided
            if 'confidence_threshold' in data:
                threshold = float(data['confidence_threshold'])
                set_confidence_threshold(threshold)
                updated_settings.append(f"confidence_threshold: {threshold}")
            
            # Update model path if provided
            if 'model_path' in data:
                model_path = data['model_path']
                set_model_path(model_path)
                updated_settings.append(f"model_path: {model_path}")
            
            message = f"Updated settings: {', '.join(updated_settings)}" if updated_settings else "No settings updated"
            
            return JsonResponse({
                'status': 'success',
                'message': message,
                'updated_settings': updated_settings,
                'config': get_yolo_config()
            })
        
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Only GET and POST methods are supported'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Error with YOLO config: {str(e)}"
        })

def yolo_management_page(request):
    """Render the YOLO management interface."""
    return render(request, 'yolo_management.html')

def current_detections_text(request):
    """Simple text endpoint for AIML to get current detections."""
    try:
        from Memory.detection_bridge import get_current_detections
        session_id = request.session.get('user_id', 'default')
        detections = get_current_detections(session_id)
        
        if detections:
            # Group objects by name
            object_counts = {}
            for detection in detections:
                name = detection['name']
                object_counts[name] = object_counts.get(name, 0) + 1
            
            # Format as simple text
            detected_objects = []
            for obj_name, count in object_counts.items():
                if count == 1:
                    detected_objects.append(f"1 {obj_name}")
                else:
                    detected_objects.append(f"{count} {obj_name}s")
            
            response_text = f"I can see: {', '.join(detected_objects)}"
        else:
            response_text = "I don't see any objects in my current field of view"
            
        return JsonResponse({
            'status': 'success',
            'detections_text': response_text,
            'object_list': list(object_counts.keys()) if detections else []
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'detections_text': "I'm having trouble accessing my vision sensors right now",
            'object_list': []
        })

def reset_drone_connection(request):
    """Manual endpoint to reset the Tello connection."""
    try:
        reset_tello_connection()
        return JsonResponse({
            'status': 'success',
            'message': 'Drone connection reset successfully. SDK mode activated.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error resetting drone connection: {str(e)}'
        })

def drone_status(request):
    """Get current drone status and connection info."""
    try:
        tel = get_tello()
        battery = tel.get_battery()
        
        # Try to get flying status
        try:
            refresh_flying_flag()
            global is_flying
            flying_status = is_flying
        except:
            flying_status = "unknown"
        
        return JsonResponse({
            'status': 'success',
            'battery': battery,
            'is_flying': flying_status,
            'connection_active': True
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error getting drone status: {str(e)}',
            'connection_active': False
        })