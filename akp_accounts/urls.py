from django.urls import path
from .views import login_attempt, logout_attempt, register_attempt, newsletter_subscribers, verify_account

urlpatterns = [
    path('login/', login_attempt, name="login"),
    path('logout-user/', logout_attempt, name="logout"),
    path('register/', register_attempt, name="register"),
    path('newsletter/', newsletter_subscribers, name="newsletter_subscribers"),
    path('verify-account/<str:token>/', verify_account, name="verify_account"),
]
