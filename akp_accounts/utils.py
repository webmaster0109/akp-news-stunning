from django.core.mail import send_mail
from django.conf import settings

def send_verification_mail(request, email, token, otp):
    try:
        website_url = request.build_absolute_uri('/')[:-1]
        forgot_password_subject = "Your registered account needs to be verified."
        forgot_password_message = f"AKP News,\n\nHi {email}\nYour one time password is {otp}\n\nClick on the link to verify your account {website_url}/account/verify-account/{token}"
        recipient_email = email
        send_mail(subject=forgot_password_subject, message=forgot_password_message, from_email=settings.EMAIL_HOST_USER, recipient_list=[recipient_email])
    except Exception as e:
        print(f"Failed to send registration email to {recipient_email}. Error: {e}")
        return False
    
    return True

def send_registration_email(user_obj):
    subject = f'Congrats {user_obj.first_name} {user_obj.last_name}! You have done registration in AKP News Portal.'
    # Change the following line to the admin's email address
    recipient_email = f'{user_obj.email}'
    message = f"Hi {user_obj.email},\n\nYou've successfully registered! Now you can login your account.\n\n\nYour username is {user_obj.username}"

    admin_subject = f'New Registration on AKP News Portal'
    admin_message = f'User Details:\n\nUser Name: {user_obj.first_name} {user_obj.last_name}\nUser Email: {user_obj.email}\n\nThank you!\nSee your admin panel to see complete details of Users.'
    admin_email = settings.EMAIL_HOST_USER 

    try:
        send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[recipient_email])
        send_mail(subject=admin_subject, message=admin_message, from_email=settings.EMAIL_HOST_USER, recipient_list=[admin_email])
    except Exception as e:
        print(f"Failed to send registration email to {recipient_email}. Error: {e}")