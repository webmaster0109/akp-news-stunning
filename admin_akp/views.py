from django.shortcuts import render, redirect
from akp_accounts.models import CustomUser

# Create your views here.

def admin_dashboard(request):
    return render(request, template_name='admin/index.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = CustomUser.objects.filter(username=username, password=password).first()

        if not user:
            return redirect('admin_login')

        if user.is_superuser:
            return redirect('admin_dashboard')
        else:
            return redirect('admin_login')

    return render(request, template_name='admin/login.html')