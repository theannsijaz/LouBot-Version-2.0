import re
import datetime
from .views import *
from .models import *
from neomodel import db
from datetime import datetime

def search_ip(request,email):
    temp = ''
    response = ''
    try:
        main_user = Signups.nodes.get(email=email)
        first_ip = main_user.ip
        first_mail_1 = main_user.email
        search = Signups.nodes.exclude(email=email)
        for user in search:
            if user.ip == first_ip:
                temp = user.username
                if check_befor_asking(request,first_mail_1,temp):
                    response = f'Do you know {temp}?'
                    break
        return response

    except Signups.DoesNotExist:
        return False

def get_after_know(s):
    parts = s.split("know")
    if len(parts) > 1:
        name_part = parts[1].strip()
        if '?' in name_part:
            name_part = name_part.split('?')[0].strip()
        return name_part
    else:
        return ""

def get_last_bot_response(session_history_data):
    bot_responses = [chat_message for chat_message in session_history_data.memory_list if chat_message.split(" - ")[1].startswith("Bot:")]
    last_two_bot_responses = bot_responses[-2:]
    print(last_two_bot_responses)

    second_last_response = last_two_bot_responses[1] if last_two_bot_responses else None

    te = second_last_response.split(" - ")[1]
    refine = te.split(": ")[-1]
    refined = get_after_know(refine)

    return refined

def check_befor_asking(request,mail,name2):
    results = ''
    meta = ''
    session = request.session.get('user_id')
    email = mail
    params = {"name2": name2,"email": email,"session":session}

    cypher_query = f"""
    MATCH (p:Signups {{email:$email}})
    MATCH (s:SocialNetwork {{name:$name2,uid:$session}})
    MATCH (p)-[r]-(s)
    RETURN r; """

    try:
        results, meta = db.cypher_query(cypher_query, params)
        print('Length of Result',len(results))
    except Exception as e:
        print(e)

    if len(results) == 0:
        return True
    else:
        return False