from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('chat/', views.chat, name='chat'),
    path('signup_login/<str:action>', views.signup_login, name='signup_login'),
    path('signout', views.signout, name='signout'),
    path('contact', views.contact, name='contact'),
    path('speech_to_text', views.speech_to_text, name='speech_to_text'),
    path('forgot1', views.forgot1, name='forgot1'),
    path('otpverifcation',views.otpverifcation,name='otpverifcation'),
    path('forgot3',views.forgot3,name='forgot3'),
    path('about',views.about,name='about'),
    path('contact',views.contact,name='contact'),
    path('upload-profile-pic/', views.upload_profile_pic, name='upload-profile-pic'),
    path('upload-data', views.upload_data, name='upload-data'),
    path('prolog_handling', views.prolog_handling, name='prolog_handling'),
    
    # WebAuthn Face ID/Touch ID routes
    path('webauthn/register/begin', views.webauthn_register_begin, name='webauthn_register_begin'),
    path('webauthn/register/complete', views.webauthn_register_complete, name='webauthn_register_complete'),
    path('webauthn/auth/begin', views.webauthn_auth_begin, name='webauthn_auth_begin'),
    path('webauthn/auth/complete', views.webauthn_auth_complete, name='webauthn_auth_complete'),
    path('webauthn/check-support', views.webauthn_check_support, name='webauthn_check_support'),
]