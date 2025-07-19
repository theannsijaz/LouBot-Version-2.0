from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import speech_recognition as sr
import base64
import io
import os
import tempfile


@csrf_exempt
def speech_to_text(request):
    """
    Handle speech-to-text conversion from either:
    1. Web Speech API (just returns success since recognition happens in browser)
    2. Audio file upload
    """
    if request.method == 'POST':
        # Check if this is a file upload
        if request.FILES.get('audio'):
            return handle_audio_file(request)
        
        # Check if this is base64 audio data
        elif request.body:
            return handle_base64_audio(request)
        
        # For Web Speech API, recognition happens in browser
        # Just return success response
        else:
            return JsonResponse({
                'status': 'success',
                'message': 'Speech recognition handled by browser'
            })
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def handle_audio_file(request):
    """Handle audio file upload and convert to text"""
    try:
        audio_file = request.FILES['audio']
        r = sr.Recognizer()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Process the audio file
        with sr.AudioFile(temp_file_path) as source:
            audio_data = r.record(source)
            try:
                text = r.recognize_google(audio_data, language='en-IN', show_all=True)
                
                if isinstance(text, dict) and 'alternative' in text:
                    return_text = ""
                    for num, alternative in enumerate(text['alternative']):
                        return_text += f"{num + 1}) {alternative['transcript']}\n"
                else:
                    return_text = str(text)
                    
            except sr.UnknownValueError:
                return_text = "Sorry! Could not understand the audio"
            except sr.RequestError as e:
                return_text = f"Sorry! Error with the speech recognition service: {e}"
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return HttpResponse(return_text)
        
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return HttpResponse("Sorry! Error processing audio file")


def handle_base64_audio(request):
    """Handle base64 encoded audio data"""
    try:
        audio_data = request.body
        audio_binary = base64.b64decode(audio_data)
        r = sr.Recognizer()
        
        with io.BytesIO(audio_binary) as audio_file:
            # Note: This approach has limitations with BytesIO
            # Better to save as temporary file first
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_binary)
                temp_file_path = temp_file.name
            
            with sr.AudioFile(temp_file_path) as source:
                audio_data = r.record(source)
                try:
                    text = r.recognize_google(audio_data, language='en-IN', show_all=True)
                    
                    if isinstance(text, dict) and 'alternative' in text:
                        return_text = ""
                        for num, alternative in enumerate(text['alternative']):
                            return_text += f"{num + 1}) {alternative['transcript']}\n"
                    else:
                        return_text = str(text)
                        
                except sr.UnknownValueError:
                    return_text = "Sorry! Could not understand the audio"
                except sr.RequestError as e:
                    return_text = f"Sorry! Error with the speech recognition service: {e}"
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
        return HttpResponse(return_text)
        
    except Exception as e:
        print(f"Error processing base64 audio: {e}")
        return HttpResponse("Sorry! Error processing audio data")


