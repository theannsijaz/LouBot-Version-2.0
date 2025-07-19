import time
def set_session(request, key, value):
    """
    Sets a session variable with an associated timestamp.
    """
    request.session[key] = value
    request.session[f"{key}_timestamp"] = time.time()

def get_session_with_expiry(request, key, expiry=120):
    """
    Retrieves a session variable, deleting it if it has expired.
    """
    timestamp_key = f"{key}_timestamp"
    
    # Check if the session variable and its timestamp exist
    if key in request.session and timestamp_key in request.session:
        creation_time = request.session[timestamp_key]
        current_time = time.time()
        
        # If more than 'expiry' seconds have passed since creation, delete the session variable
        if current_time - creation_time > expiry:
            del request.session[key]
            del request.session[timestamp_key]
            return None
        
        return request.session[key]
    
    return None