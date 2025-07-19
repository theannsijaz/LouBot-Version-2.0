from django.http import HttpResponse ,JsonResponse,HttpResponseBadRequest
from django.shortcuts import render,redirect
from .views import *
from .decorators import *
from .session import *
from .models import *
import random

def generate_random_otp():
    otp = ''.join(random.choices('0123456789', k=6))
    return otp

def forgot1(request):
    if request.method == 'POST':
        email_user = request.POST['email']
        print(email_user)
        if not email_user:
            return JsonResponse({'message': 'Email is required'}, status=400)
        try:
            otppassword = generate_random_otp()

            print(otppassword)
            useremail = "annsijaz@outlook.com"  
            set_session(request, "userOTP", otppassword)
            set_session(request, "email", email_user)
            a = Signups.nodes.filter(email = email_user).first()
            send_otp(request, otppassword, useremail,a.username)
            return redirect('otpverifcation')

        except Exception as e:
            return JsonResponse({'status': 'An unexpected error occurred'}, status=500)

    return render(request, 'reset-password.html')

@requires_forgot1
def otpverifcation(request):
    if request.method == 'POST':
        opt =request.POST['otp']
        try:
            otpUser =  get_session_with_expiry(request , 'userOTP')
            email =  get_session_with_expiry(request , 'email')
            if otpUser is None: 
                return HttpResponse('The Otp expired')
            else:
                if int(opt) == int(otpUser):
                    return redirect('forgot3')
                else: 
                    return HttpResponse('Wrong OTP')
        except Exception as e:
            print("3 pass 3")

    return render(request, 'otp.html')

@requires_otp_verification
def forgot3(request):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = get_session_with_expiry(request, 'email')

        if email and new_password and confirm_password and new_password == confirm_password:
            try:
                staff_member = Signups.nodes.get(email=email)
                staff_member.password = new_password
                staff_member.save()
                send_success(request,staff_member.email,staff_member.username)
                return redirect('login')
            except Signups.DoesNotExist:
                return HttpResponse('User not found. Please try again.')
            except Exception as e:
                return HttpResponse(f'An error occurred: {str(e)}')
        else:
            return HttpResponse('Passwords do not match. Please try again.')

    return render(request, 'new_password.html')