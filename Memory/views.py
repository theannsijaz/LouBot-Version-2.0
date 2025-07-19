from django.http import HttpResponse ,JsonResponse,HttpResponseBadRequest
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Sensory_Memory.views import get_command
from django.shortcuts import render,redirect
from django.contrib.auth import logout
from datetime import datetime, date
from django.contrib import messages
from googletrans import Translator
from Sensory_Memory.views import *
from .Social_Network import *
from .Update_Store import *
from Memory.models import *
from .decorators import *
from neomodel import db
from neomodel import *
from .prolog import *
from .Emails import *
from .models import *
from .Speech import *
from .aiml import *
from .nlp import *
from .OTP import *
from .webauthn_utils import WebAuthnUtils
from .gender_names_db import detect_gender_from_name
from .detection_bridge import get_current_detections as bridge_get_detections
import re

kernel = init_kernel()
translator = Translator()
urdu_pattern = r'^[\u0600-\u06FF\s]+$'


def index(request):
    session = request.session.get('user_id')
    faq = FAQS.objects.all()
    return render(request,'index.html',{'session':session,'faq':faq})

def login(request):
    return render(request, 'login.html')   

def signup_login(request, action=None):
    face_id = None
    if request.method == "POST":
        if action == 'signup':
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            dob_str = request.POST.get('dob')
            ip_address = request.POST.get('ip_address')
            print(ip_address)
            
            # Check for duplicate email
            try:
                existing_user = Signups.nodes.get(email=email)
                if existing_user:
                    return HttpResponseBadRequest("An account with this email already exists.")
            except Signups.DoesNotExist:
                # Email doesn't exist, proceed with signup
                pass
            
            if dob_str:
                try:
                    dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                except ValueError:
                    return HttpResponseBadRequest("Invalid date format for date of birth.")
            else:
                return HttpResponseBadRequest("Date of birth is required.")
            
            # Detect gender from name using names database
            gen = detect_gender_from_name(name)
            user = Signups(username=name, email=email, password=password, dob=dob, gender=gen,ip=ip_address)
            user.save()
            msg = "We are delighted to welcome you to our community! Your registration is confirmed, and we are excited to have you on board."
            user_element_id = user.element_id
            split_element_id = user_element_id.split(":")
            face_id = split_element_id[-1]
            user.uid = face_id
            user.face_id = True
            user.save()
            Signup_Thanks(name,email,msg)
            print("Id===", face_id)
            request.session['user_id'] = user.uid
            return redirect('index')
        else:
            if action == 'login':
                mail = request.POST.get('emailid')
                passcode = request.POST.get('password')
                ip_address = request.POST.get('ip_address')
                print(ip_address)
                
                try:
                    user = Signups.nodes.get(email=mail, password=passcode)
                    print('working')
                    print(user.uid)
                    request.session['user_id'] = user.uid
                    Login_Trigger(user.username,mail)
                    if user:
                        user.ip = ip_address
                        user.save()
                        return redirect('index')
                    else:
                        return HttpResponse('Wrong Email or Password')
                except Signups.DoesNotExist:
                    return HttpResponse('Wrong Email or Password')
                     
    return render(request, 'login.html')

def contact(request):
    return render(request,'contact-us.html')

def signout(request):
    logout(request)
    request.session.flush()
    return redirect('index')

def about(request):
    session = request.session.get('user_id')
    return render(request,'service.html',{'session':session})


def contact(request):
    session = request.session.get('user_id')
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        message = request.POST['message']
        try:
            if session:
                contact = Contact(name=name, email=email, phone_number=phone_number, message=message)
                contact.save()
                messages.success(request, 'Your message has been submitted successfully!')
                send_success_contact(request,email,name,message)
                return redirect('index')
            else:
                return redirect('login')
        except Exception as e:
            return HttpResponse('An error occurred while processing your request.')

    return render(request,'contact-us.html',{'session':session})

# =======================================================================================================
def sentiment(text):
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    
    if scores['compound'] >= 0.05:
        sentiments = 'Positive sentiments'
    elif scores['compound'] <= -0.05:
        sentiments = 'Negative sentiments'
    else:
        sentiments = 'Neutral sentiments'
        
    return sentiments

def process_sentiment(text):
    chat_data = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - (User|Bot): ', '', text)
    return chat_data

def update_sentiment(text):
    data = process_sentiment(text)
    update = sentiment(data)
    return update


def maintain_history(request, user, bot):
    user_id = request.session.get('user_id')
    user_node = Signups.nodes.filter(uid=user_id).first()
    
    try:
        history_chat_node = History_Chat.nodes.filter(uid=user_id).first()
    except:
        history_chat_node = History_Chat(uid=user_id, name="History").save()
        user_node.chat.connect(history_chat_node)

    session_history_node = None
    
    if history_chat_node:
        start_session = datetime.combine(date.today(), datetime.min.time())
        try:
            name = f"Episode - {start_session.strftime('%Y-%m-%d')}" 
            session_history_node = Session_History.nodes.get(uid=user_id, name=name)
        except:
            name = f"Episode - {start_session.strftime('%Y-%m-%d')}" 
            session_history_node = Session_History(uid=user_id, name=name).save()
            history_chat_node.history.connect(session_history_node)

    if session_history_node:
        session_history_node.save_message("User", user)
        session_history_node.save_message("Bot", bot)
        data = '\n'.join(session_history_node.memory_list)
        new_sent = update_sentiment(data)
        print('-=======================================-0-90-8908-97-07-87-87870896-968709',new_sent)
        session_history_node.overall_sentiments = new_sent
        session_history_node.save()


def extend_episode(request,user,bot,session):
    today = datetime.now().strftime('%Y-%m-%d')
    check = f"Episode - {today}"
    obj_ep = Session_History.nodes.get(uid = session,name = check)
    try:
        s1 = sentiment(bot)
        s2 = sentiment(user)
        user_obj = Episode_Part(uid = session,name='Bot',response=bot,sentiments=s1).save()
        bot_bot = Episode_Part(uid = session,name='User',response=user,sentiments=s2).save()
        user_obj.relation.connect(obj_ep)
        bot_bot.relation.connect(obj_ep)
    except:
        print('Error')

def get_relationship_graph_data(name, relation, session):
    """Get graph data for relationship visualization"""
    try:
        # Get the main person and their relationships
        params = {"name": name, "relation": relation, "session": session}
        
        # Query to get the relationship network around the person
        cypher_query = f"""
            MATCH (p:Person {{uid: $session, full_name: $name}})
            MATCH (p)<-[r:`{relation}`]-(other)
            RETURN p.full_name as person, other.full_name as related_person, type(r) as relationship_type
            UNION
            MATCH (p:Person {{uid: $session, full_name: $name}})
            MATCH (p)-[r:`{relation}`]->(other)
            RETURN p.full_name as person, other.full_name as related_person, type(r) as relationship_type
        """
        
        results, meta = db.cypher_query(cypher_query, params)
        
        nodes = []
        links = []
        node_ids = set()
        
        # Add the main person node
        nodes.append({
            'id': name,
            'label': name.title(),
            'type': 'main'
        })
        node_ids.add(name)
        
        # Process relationships
        for result in results:
            person, related_person, relationship_type = result
            
            # Add related person node if not already added
            if related_person not in node_ids:
                nodes.append({
                    'id': related_person,
                    'label': related_person.title(),
                    'type': 'related'
                })
                node_ids.add(related_person)
            
            # Add link
            links.append({
                'source': person,
                'target': related_person,
                'relationship': relationship_type,
                'label': relationship_type.replace('_', ' ').title()
            })
        
        return {
            'nodes': nodes,
            'links': links
        }
        
    except Exception as e:
        print(f"Error getting graph data: {e}")
        return {'nodes': [], 'links': []}

# ========================================================================================================

def chat(request):    
    session = request.session.get('user_id')
    try:
        current_user = Signups.nodes.filter(uid = session).first()
    except:
        return redirect('login')
    Session_History.nodes.filter(uid = session)
    try:
        if session:
            user = Signups.nodes.filter(uid=session).get()
        else:
            messages.error(request, 'You must log in to access the chat.')
            return redirect('index')
    except:
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('index')

    if request.method == 'POST':
        message = request.POST.get('message', '')
        kernel.setPredicate('name',user.username)
        kernel.setPredicate('gender',user.gender)
        if message:
            # Clear any lingering relationship predicates BEFORE processing
            kernel.setPredicate("namex", "")
            kernel.setPredicate("relationx", "")
            kernel.setPredicate("namey", "")
            
            # Process the message once
            if  re.match(urdu_pattern, message):
                english = translator.translate(message).text
                bot_response = kernel.respond(english)
                bot_response = translator.translate(bot_response, dest='ur').text
            else:
                bot_response = kernel.respond(message)
                
            print("Predicates:",
                    kernel.getPredicate("moveforward"),
                    kernel.getPredicate("movebackward"),
                    kernel.getPredicate("moveleft"),
                    kernel.getPredicate("moveright"))
            
            # Debug: Print all relationship predicates
            print("Relationship predicates after initial processing:",
                  "namex:", kernel.getPredicate("namex"),
                  "relationx:", kernel.getPredicate("relationx"),
                  "namey:", kernel.getPredicate("namey"))

            if kernel.getPredicate("namex") and kernel.getPredicate("relationx"):
                print("Processing relationship query:", kernel.getPredicate("namex"), kernel.getPredicate("relationx"))
                name = kernel.getPredicate("namex").lower()
                relation = kernel.getPredicate("relationx").lower()

                # Clear the predicates immediately to prevent persistence
                kernel.setPredicate("namex", "")
                kernel.setPredicate("relationx", "")

                params = {"name": name,"relation": relation}
                cypher_query = f"""
                    MATCH (p:Person {{full_name: $name}})
                    MATCH (p)<-[r:`{relation}`]-(other)
                    RETURN other.full_name; """
                results, meta = db.cypher_query(cypher_query, params)

                # Get graph data for visualization only if we have results
                graph_data = None
                if results:
                    graph_data = get_relationship_graph_data(name, relation, session)

                if results:
                    formatted_names = []
                    for result in results:
                        other_name = result[0]
                        formatted_names.append(other_name)
                    if len(formatted_names) == 1:
                        name_str = formatted_names[0]
                    elif len(formatted_names) == 2:
                        name_str = f"{formatted_names[0]} and {formatted_names[1]}"
                    else:
                        name_str = ', '.join(formatted_names[:-1]) + f", and {formatted_names[-1]}"

                    if name_str != '':
                        kernel.setPredicate('namey',name_str.capitalize())
                        # Generate final response with the relationship data
                        bot_response = kernel.respond(message)
                        
                        # Clear namey predicate after use
                        kernel.setPredicate('namey', '')
                        
                        # Return response with graph data only if relationships exist
                        bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                        maintain_history(request, message, bot_response)
                        extend_episode(request,message,bot_response,session)
                        return JsonResponse({
                            'bot_response': bot_response,
                            'graph_data': graph_data
                        })
                else:
                    bot_response = 'No knowledge Found in knowledgebase according to your Query.'
                    
                # Return without graph data when no relationships found
                bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                maintain_history(request, message, bot_response)
                extend_episode(request,message,bot_response,session)
                return JsonResponse({
                    'bot_response': bot_response
                })

            elif kernel.getPredicate("person_sn") and kernel.getPredicate("relation_sn"):
                person_sn = kernel.getPredicate("person_sn")
                relation_sn = kernel.getPredicate("relation_sn")
                # Detect gender from person name using names database
                gender = detect_gender_from_name(person_sn)

                today_date = datetime.now().strftime('%Y-%m-%d')
                chk_date = f"Episode - {today_date}"
                session_history_data = Session_History.nodes.get(name=chk_date,uid=session)

                last_two_bot_responses = get_last_bot_response(session_history_data)
                name = get_last_bot_response(session_history_data)
                top = Signups.nodes.get(uid=session)
                email1 = top.email

                # Detect gender from name using names database
                gen = detect_gender_from_name(name)

                params = {"name": name,"relation_sn": relation_sn,"email1":email1,"session":session}

                print(params)
                if params:
                    print('Access')
                    cypher_query = f"""
                        MATCH (p:Signups {{email:$email1}})
                        CREATE (s:SocialNetwork {{name:$name,uid:$session}})
                        CREATE (p)<-[r:`is_{relation_sn}`]-(s)
                        RETURN r; """ 
                    results, meta = db.cypher_query(cypher_query, params)

                    print(results,meta)

            elif kernel.getPredicate("takeoff"):
                # Execute take-off only once and then clear the flag so it
                # won't block MOVE commands that follow.
                get_command(message, session)
                takeoff_result = Tello_Takeoff()
                kernel.setPredicate("takeoff", "")
                
                # If takeoff returns a battery warning, use that as the response
                if takeoff_result and "Battery too low" in takeoff_result:
                    bot_response = takeoff_result
                
                bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                return JsonResponse({'bot_response': bot_response})


            elif kernel.getPredicate("turnon") or kernel.getPredicate("sec"):
                get_command(message, session)
                warmup_result = None
                if kernel.getPredicate("sec"):
                    val = kernel.getPredicate("sec")
                    warmup_result = warmup(val)
                    kernel.setPredicate("sec", "")
                else:
                    warmup_result = warmup(None)
                kernel.setPredicate("turnon", "")
                
                # If warmup returns a battery warning or other message, use that as the response
                if warmup_result and ("Battery too low" in warmup_result or "Already airborne" in warmup_result or "completed successfully" in warmup_result):
                    bot_response = warmup_result
                
                bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                return JsonResponse({'bot_response': bot_response})




        
            elif kernel.getPredicate("land"):
                get_command(message, session)
                land_result = Tello_Land()
                kernel.setPredicate("land", "")
                
                # If landing returns a status message, use that as the response
                if land_result:
                    bot_response = land_result
                
                bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                return JsonResponse({'bot_response': bot_response})


            elif kernel.getPredicate("moveforward"):
                get_command(message, session)
                value = kernel.getPredicate("moveforward")
                move_result = Move_Forward(value)
                kernel.setPredicate("moveforward", "")
                
                if move_result:
                    bot_response = move_result
                
                bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                return JsonResponse({'bot_response': bot_response})

            elif kernel.getPredicate("movebackward"):
                get_command(message, session)
                value = kernel.getPredicate("movebackward")
                move_result = Move_Backward(value)
                kernel.setPredicate("movebackward", "")
                
                if move_result:
                    bot_response = move_result
                
                bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                return JsonResponse({'bot_response': bot_response})

            elif kernel.getPredicate("moveleft"):
                get_command(message, session)
                value = kernel.getPredicate("moveleft")
                move_result = Move_Left(value)
                kernel.setPredicate("moveleft", "")
                
                if move_result:
                    bot_response = move_result
                
                bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                return JsonResponse({'bot_response': bot_response})

            elif kernel.getPredicate("moveright"):
                get_command(message, session)
                value = kernel.getPredicate("moveright")
                move_result = Move_Right(value)
                kernel.setPredicate("moveright", "")
                
                if move_result:
                    bot_response = move_result
                
                bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
                return JsonResponse({'bot_response': bot_response})

            default_message = "I'm sorry, I didn't understand what you said."
            if bot_response == default_message or default_message in bot_response or bot_response.endswith("I didn't understand what you said.") or bot_response=='' or bot_response=='I do not understand. What is your occupation?':
                chk = search_ip(request,current_user.email)
                print('shkcgsdg',chk)
                if chk:
                    print('hgjkHJ')
                    bot_response = chk
                else:
                    bot_response = "I'm here to help! You can ask me about what I can see, check my sensors, or chat about various topics. Try asking 'what can you see' or 'battery status'."
            
            bot_response = process_dynamic_response(bot_response, request.session.get('user_id', 'default'))
            maintain_history(request, message, bot_response)
            extend_episode(request,message,bot_response,session)
            return JsonResponse({'bot_response': bot_response})

    return render(request, 'chat_new.html',{'current_user':current_user})

@csrf_exempt
def prolog_handling(request):
    if request.method == 'POST':
        prolog_file = request.FILES.get('prolog_file')
        if prolog_file:
            # Call the actual prolog_handling function from prolog.py
            from .prolog import prolog_handling as prolog_handler
            return prolog_handler(request)
    return JsonResponse({'error': 'No file uploaded'})

def upload_profile_pic(request):
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            # Handle profile picture upload
            pass
    return redirect('chat')

def upload_data(request):
    if request.method == 'POST':
        # Handle data upload
        pass
    return redirect('chat')

def forgot1(request):
    return render(request, 'reset-password.html')

def otpverifcation(request):
    return render(request, 'otp.html')

def forgot3(request):
    return render(request, 'new_password.html')

def take_picture(request):
    return JsonResponse({'status': 'success'})

def drone_video_feed(request):
    # This should return the drone video feed
    return HttpResponse('Video feed placeholder')

# Import speech_to_text from Speech module
from .Speech import speech_to_text

# ========================================================================================================
# WebAuthn Face ID/Touch ID Authentication Views
# ========================================================================================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .webauthn_utils import WebAuthnUtils
from .models import WebAuthnCredential
import json
import base64

@csrf_exempt
@require_POST
def webauthn_register_begin(request):
    """Begin WebAuthn registration"""
    try:
        session = request.session.get('user_id')
        if not session:
            print("[WebAuthn] Begin registration failed: Not authenticated")
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        user = Signups.nodes.filter(uid=session).first()
        if not user:
            print(f"[WebAuthn] Begin registration failed: User not found for session {session}")
            return JsonResponse({'error': 'User not found'}, status=404)
        
        print(f"[WebAuthn] Starting registration for user {user.email}")
        
        # Generate registration options
        options = WebAuthnUtils.create_registration_options(
            user_id=session,
            username=user.email,
            display_name=user.username
        )
        
        # Store challenge in session
        user.challenge = options['challenge_b64']
        user.save()
        
        print(f"[WebAuthn] Registration options generated successfully")
        
        return JsonResponse({
            'status': 'success',
            'options': options['publicKey']
        })
        
    except Exception as e:
        print(f"[WebAuthn] Begin registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def webauthn_register_complete(request):
    """Complete WebAuthn registration"""
    try:
        session = request.session.get('user_id')
        if not session:
            print("[WebAuthn] Registration failed: Not authenticated")
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        user = Signups.nodes.filter(uid=session).first()
        if not user:
            print(f"[WebAuthn] Registration failed: User not found for session {session}")
            return JsonResponse({'error': 'User not found'}, status=404)
        
        data = json.loads(request.body)
        response = data.get('response')
        
        if not response:
            print("[WebAuthn] Registration failed: Invalid response")
            return JsonResponse({'error': 'Invalid response'}, status=400)
        
        print(f"[WebAuthn] Processing registration for user {user.email}")
        
        # Verify registration response
        verification_result = WebAuthnUtils.verify_registration_response(
            response=data,
            expected_challenge=user.challenge,
            user_id=session
        )
        
        print(f"[WebAuthn] Verification successful, saving credential")
        
        # Save credential
        credential = WebAuthnCredential(
            uid=session,
            credential_id=verification_result['credential_id'],
            public_key=verification_result['public_key'],
            sign_count=verification_result['sign_count'],
            aaguid=verification_result['aaguid'],
            transports=verification_result['transports'],
            device_name=f"Mac Touch ID/Face ID"
        ).save()
        
        # Link credential to user
        user.webauthn_credentials.connect(credential)
        user.webauthn_enabled = True
        user.challenge = ""  # Clear challenge
        user.save()
        
        print(f"[WebAuthn] Registration complete for user {user.email}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Face ID/Touch ID registration successful!'
        })
        
    except Exception as e:
        print(f"[WebAuthn] Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST 
def webauthn_auth_begin(request):
    """Start WebAuthn authentication"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email required'}, status=400)
        
        user = Signups.nodes.filter(email=email).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Get user's credentials
        credentials = user.webauthn_credentials.all()
        credential_ids = [cred.credential_id for cred in credentials if cred.is_active]
        
        if not credential_ids:
            return JsonResponse({'error': 'No Face ID/Touch ID credentials found'}, status=404)
        
        # Create authentication options
        options = WebAuthnUtils.create_authentication_options(credential_ids)
        
        # Store challenge
        user.challenge = options['challenge_b64']
        user.save()
        
        return JsonResponse({
            'status': 'success',
            'options': options['publicKey']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def webauthn_auth_complete(request):
    """Complete WebAuthn authentication"""
    try:
        data = json.loads(request.body)
        response = data.get('response')
        email = data.get('email')
        
        if not response or not email:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        user = Signups.nodes.filter(email=email).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Find the credential
        credential_id = data.get('rawId', '')
        credential = None
        for cred in user.webauthn_credentials.all():
            if cred.credential_id == credential_id:
                credential = cred
                break
        
        if not credential:
            return JsonResponse({'error': 'Credential not found'}, status=404)
        
        # Verify authentication response
        verification_success = WebAuthnUtils.verify_authentication_response(
            response=data,
            expected_challenge=user.challenge,
            stored_public_key=credential.public_key,
            stored_sign_count=credential.sign_count
        )
        
        if verification_success:
            # Update credential
            credential.update_last_used()
            
            # Log in user
            request.session['user_id'] = user.uid
            user.challenge = ""  # Clear challenge
            user.save()
            
            # Send login notification
            Login_Trigger(user.username, user.email)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Authentication successful!',
                'redirect': '/chat'
            })
        else:
            return JsonResponse({'error': 'Authentication failed'}, status=401)
        
    except Exception as e:
        return JsonResponse({'error': f'Authentication failed: {str(e)}'}, status=500)

@require_GET
def webauthn_check_support(request):
    """Check if WebAuthn is supported and get user's credential status"""
    try:
        session = request.session.get('user_id')
        has_credentials = False
        
        if session:
            user = Signups.nodes.filter(uid=session).first()
            if user:
                credentials = user.webauthn_credentials.all()
                has_credentials = len([c for c in credentials if c.is_active]) > 0
        
        return JsonResponse({
            'webauthn_supported': True,  # Assume modern browsers support it
            'has_credentials': has_credentials,
            'platform_authenticator_available': True  # Will be checked on frontend
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def process_dynamic_response(bot_response, request_session_id=None):
    """
    Process bot response and replace placeholders with actual dynamic data
    """
    if not bot_response or '{{' not in bot_response:
        return bot_response
    
    # Import detection functions
    from Memory.detection_bridge import get_current_detections
    
    # Get current detections
    detections = get_current_detections(request_session_id)
    
    # Replace detection placeholders
    if '{{CURRENT_DETECTIONS}}' in bot_response:
        if detections:
            detection_text = "I can see: " + ", ".join([obj['name'] for obj in detections])
            bot_response = bot_response.replace('{{CURRENT_DETECTIONS}}', detection_text)
        else:
            bot_response = bot_response.replace('{{CURRENT_DETECTIONS}}', "I don't see any objects in my current field of view.")
    
    # Replace object checking placeholders
    if '{{CHECK_OBJECT_' in bot_response:
        import re
        pattern = r'\{\{CHECK_OBJECT_([^}]+)\}\}'
        matches = re.findall(pattern, bot_response)
        for match in matches:
            object_name = match.replace('*', '').lower().strip()
            if detections:
                found = any(object_name in obj['name'].lower() for obj in detections)
                if found:
                    response_text = f"Yes, I can see a {object_name} in my field of view!"
                else:
                    response_text = f"No, I don't see any {object_name} right now."
            else:
                response_text = f"I don't see any {object_name}. My visual sensors are not detecting anything currently."
            bot_response = bot_response.replace(f'{{{{CHECK_OBJECT_{match}}}}}', response_text)
    
    # Replace object counting placeholders
    if '{{COUNT_OBJECTS_' in bot_response:
        import re
        pattern = r'\{\{COUNT_OBJECTS_([^}]+)\}\}'
        matches = re.findall(pattern, bot_response)
        for match in matches:
            object_name = match.replace('*', '').lower().strip().rstrip('s')  # Remove plural 's'
            if detections:
                count = sum(1 for obj in detections if object_name in obj['name'].lower())
                if count > 0:
                    plural = 's' if count != 1 else ''
                    response_text = f"I can see {count} {object_name}{plural}."
                else:
                    response_text = f"I don't see any {object_name}s in my current field of view."
            else:
                response_text = f"I don't see any {object_name}s. My visual sensors are not detecting anything right now."
            bot_response = bot_response.replace(f'{{{{COUNT_OBJECTS_{match}}}}}', response_text)
    
    # Replace vision status placeholder
    if '{{VISION_STATUS}}' in bot_response:
        try:
            from Sensory_Memory.detection_config import is_yolo_enabled
            from Sensory_Memory.yolo_detector import get_yolo_detector
            
            if is_yolo_enabled():
                detector = get_yolo_detector()
                if detector.is_available():
                    if detections:
                        response_text = f"Yes, my vision system is working perfectly! I can currently see {len(detections)} objects."
                    else:
                        response_text = "Yes, my vision system is operational but I don't see any objects right now."
                else:
                    response_text = "My vision system is enabled but not functioning properly right now."
            else:
                response_text = "My vision system is currently disabled."
        except:
            response_text = "I cannot check my vision system status right now."
        bot_response = bot_response.replace('{{VISION_STATUS}}', response_text)
    
    # Replace sensor data placeholders
    try:
        from Sensory_Memory.views import fetch_drone_data
        drone_data = fetch_drone_data()
        
        if '{{BATTERY_LEVEL}}' in bot_response:
            response_text = f"My battery level is at {drone_data['battery']}%."
            bot_response = bot_response.replace('{{BATTERY_LEVEL}}', response_text)
        
        if '{{TEMPERATURE}}' in bot_response:
            response_text = f"The temperature range is {drone_data['temperature_range']}. Lowest: {drone_data['lowest_temperature']}°C, Highest: {drone_data['highest_temperature']}°C."
            bot_response = bot_response.replace('{{TEMPERATURE}}', response_text)
        
        if '{{CURRENT_HEIGHT}}' in bot_response:
            response_text = f"I am currently at a height of {drone_data['height']} cm above the ground."
            bot_response = bot_response.replace('{{CURRENT_HEIGHT}}', response_text)
        
        if '{{CURRENT_SPEED}}' in bot_response:
            response_text = f"My current speed is {drone_data['speed']} cm/s."
            bot_response = bot_response.replace('{{CURRENT_SPEED}}', response_text)
        
        if '{{FLIGHT_TIME}}' in bot_response:
            flight_time = drone_data['flight_time']
            minutes = flight_time // 60
            seconds = flight_time % 60
            if minutes > 0:
                response_text = f"I have been flying for {minutes} minutes and {seconds} seconds."
            else:
                response_text = f"I have been flying for {seconds} seconds."
            bot_response = bot_response.replace('{{FLIGHT_TIME}}', response_text)
        
        if '{{BAROMETER}}' in bot_response:
            response_text = f"The barometric pressure is {drone_data['barometer']} mbar."
            bot_response = bot_response.replace('{{BAROMETER}}', response_text)
            
    except Exception as e:
        # Replace any remaining sensor placeholders with error messages
        sensor_placeholders = ['{{BATTERY_LEVEL}}', '{{TEMPERATURE}}', '{{CURRENT_HEIGHT}}', 
                             '{{CURRENT_SPEED}}', '{{FLIGHT_TIME}}', '{{BAROMETER}}']
        for placeholder in sensor_placeholders:
            if placeholder in bot_response:
                bot_response = bot_response.replace(placeholder, "I cannot access sensor data right now.")
    
    return bot_response