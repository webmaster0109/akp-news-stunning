from django.urls import path
from .views import login_attempt, logout_attempt, register_attempt

urlpatterns = [
    path('login/', login_attempt, name="login"),
    path('logout-user/', logout_attempt, name="logout"),
    path('register/', register_attempt, name="register"),
]
