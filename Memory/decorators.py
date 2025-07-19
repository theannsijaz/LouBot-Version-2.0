# from functools import wraps
from django.shortcuts import redirect
from .models import *
from .session import *
from .urls import *
from django.http import JsonResponse,HttpResponse


def requires_forgot1(view_func):
    def wrapper(request, *args, **kwargs):
        if 'email' not in request.session or 'userOTP' not in request.session:
            if request.resolver_match.url_name != 'forgot1':
                return redirect('forgot1')
        return view_func(request, *args, **kwargs)
    return wrapper

def requires_otp_verification(view_func):
    def wrapper(request, *args, **kwargs):
        if 'email' not in request.session or 'userOTP' not in request.session:
            if request.resolver_match.url_name != 'otpverifcation':
                return redirect('forgot1')
        return view_func(request, *args, **kwargs)
    return wrapper
