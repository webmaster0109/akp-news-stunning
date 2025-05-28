from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import CustomUser
# Create your views here.


def login_attempt(request):

    if request.method == "POST":
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            if not username or not password:
                return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)
            
            user_obj = authenticate(request, username=username, password=password)

            if user_obj:
                login(request, user_obj)
                return JsonResponse({'status': 'success', 'message': 'login successfully'}, status=200)
            
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
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists'}, status=400)
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists'}, status=400)
        
        user_obj = CustomUser.objects.create_user(username=email.split('@')[0], email=email, password=password)
        user_obj.save()
        return JsonResponse({'status': 'success', 'message': 'User created successfully'}, status=200)

    return render(request, template_name="register.html")