from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import CustomUser, NewsletterSubscriber
import random
import uuid
from .utils import send_verification_mail, send_registration_email
# Create your views here.


def login_attempt(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)
            
        user_obj = authenticate(request, username=str(email).split('@')[0], password=password)

        if user_obj:
            login(request, user_obj)
            return JsonResponse({'status': 'success', 'message': 'login successfully'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
        
    if request.user.is_authenticated:
        return redirect('index_akp_news')
        
    return render(request, template_name="login.html")

def logout_attempt(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid method requested'}, status=401)
    logout(request)
    return JsonResponse({'status': 'success', 'message': 'logging out...'}, status=200)


def register_attempt(request):

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not first_name or not last_name or not email or not password:
            return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)
        
        if CustomUser.objects.filter(username=str(email).split('@')[0]).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists'}, status=400)
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists'}, status=400)
        
        otp = random.randint(100000, 999999)
    
        user_obj = CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=str(email).split('@')[0], 
            email=email,
            verification_otp=otp,
            verification_token=str(uuid.uuid4())
        )
        user_obj.set_password(password)
        user_obj.save()

        send_verification_mail(request, email, user_obj.verification_token, user_obj.verification_otp)

        return JsonResponse({'status': 'success', 'message': 'Verification code has been sent to mail. Please check your mail.'}, status=200)

    return render(request, template_name="register.html")

def verify_account(request, token):

    try:
        user_obj = CustomUser.objects.get(verification_token=token)
        if request.user.is_authenticated:
            return redirect('/')
        if user_obj.is_user_active:
            return JsonResponse({'status': 'error', 'message': 'Your account is already verified.'}, status=400)

        if request.method == "POST":
            otp = request.POST.get("otp")
            if len(otp) != 6:
                return JsonResponse({
                    'status': 'error',
                    'message': f"You've entered {len(otp)}-digit OTP. Please enter a valid 6-digit OTP."
                }, status=400)
            if int(otp) != user_obj.verification_otp:
                return JsonResponse({
                    'status': 'error',
                    'message': 'You have entered incorrect OTP'
                }, status=400)
            else:
                user_obj.is_user_active=True
                user_obj.verification_otp=None
                user_obj.save()
                send_registration_email(user_obj)
                login(request, user_obj)
                return JsonResponse({
                    'status': 'success',
                    'message': 'You have been successfully registered'
                }, status=200)
        
        context = {
            'user_obj': user_obj
        }

    except Exception as e:
        print(e)
    
    return render(request, template_name="account/verify_account.html", context=context)

def newsletter_subscribers(request):
    if request.method == "POST":
        email = request.POST.get('subscriber_email')

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=401)
        
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already subscribed'}, status=400)
        
        NewsletterSubscriber.objects.create(email=email)
        return JsonResponse({'status': 'success', 'message': 'Subscribed successfully'}, status=200)