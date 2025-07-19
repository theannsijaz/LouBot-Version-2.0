from django.core.mail import send_mail,BadHeaderError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import datetime


def Signup_Thanks(name, email, message):
    subject = 'Thank You for Signing Up'
    email_context = {'name': name, 'email': email, 'message': message}
    html_message = render_to_string('Thanks.html', email_context)
    recipient_list = [email]
    print(email_context)
    try:
        send_mail(subject, '', 'annsijaz@outlook.com', recipient_list, html_message=html_message, fail_silently=True)
        return True, 'Your message has been submitted successfully.'
    except Exception as e:
        return False, f'Failed to send confirmation email: {str(e)}'

def Login_Trigger(name, email):
    subject = 'Login Notification'
    login_datetime = timezone.now()
    login_datetime_local = timezone.localtime(login_datetime)
    login_date = login_datetime_local.strftime('%Y-%m-%d')
    login_time = login_datetime_local.strftime('%H:%M:%S')
    email_context = {'name': name, 'date': login_date, 'time': login_time}
    html_message = render_to_string('login_notification.html', email_context)
    recipient_list = [email]
    try:
        send_mail(subject, '', 'annsijaz@outlook.com', recipient_list, html_message=html_message, fail_silently=True)
        return True, 'Login notification sent successfully.'
    except Exception as e:
        return False, f'Failed to send login notification email: {str(e)}'

def send_otp(request, otp, email, name):
    subject = 'Password Reset OTP'
    email_context = {'otp': otp, 'name': name}
    html_message = render_to_string('otp_mail.html', email_context)    
    recipient_list = [email]
    try:
        send_mail(subject, '', 'annsijaz@outlook.com', recipient_list, html_message=html_message, fail_silently=True)
        return True, 'Your message has been submitted successfully.'
    except Exception as e:
        return False, f'Failed to send confirmation email: {str(e)}'


    # try:
    #     email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    #     email.attach_alternative(html_content, "text/html")
    #     email.send()

    #     message = "Email sent successfully"
    #     return message

    # except Exception as e:
    #     message = f"Error occurred while sending the email: {e}"
    #     return message


def send_success(request, email, name):
    subject = 'Password Updated Successfully'
    email_context = {'name': name}
    html_message = render_to_string('pass_update_successful.html', email_context)    
    recipient_list = [email]
    try:
        send_mail(subject, '', 'annsijaz@outlook.com', recipient_list, html_message=html_message, fail_silently=True)
        return True, 'Your message has been submitted successfully.'
    except Exception as e:
        return False, f'Failed to send confirmation email: {str(e)}'

def send_success_contact(request, email, name, message_summary):
    subject = 'Contact Form Submission Received'
    email_context = {'name': name, 'message_summary': message_summary}
    html_message = render_to_string('contact_successful.html', email_context)
    recipient_list = [email]
    try:
        send_mail(subject, '', 'annsijaz@outlook.com', recipient_list, html_message=html_message, fail_silently=True)
        return True, 'Your message has been submitted successfully.'
    except Exception as e:
        return False, f'Failed to send confirmation email: {str(e)}'