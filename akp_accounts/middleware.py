from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
import json


class AdminConcurrentLoginMiddleware(MiddlewareMixin):
    MAX_SESSIONS_PER_USER = 2
    CACHE_PREFIX = 'admin_sessions_'

    def process_request(self, request):
        if not request.path.startswith('/private-admin/') or not request.user.is_authenticated:
            return None
        if not request.user.is_staff:
            return None
        
        current_session_key = request.session.session_key
        if not current_session_key:
            return None
        
        self.update_session_activity(request.user.id, current_session_key, request)

        if self.check_session_limit(request.user.id, current_session_key):
            messages.error(
                request,
                'Access denied: Max 2 concurrent admin sessions are allowed per user.'
            )
            logout(request)
            return redirect(reverse('admin_login'))

        return None
    
    def update_session_activity(self, user_id, session_key, request):
        cache_key = f"{self.CACHE_PREFIX}{user_id}"
        sessions_data = cache.get(cache_key, {})

        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:200]

        sessions_data[session_key] = {
            'ip_address': ip_address,
            'user_agent': user_agent,
            'last_activity': timezone.now().isoformat()
        }

        sessions_data = self.clean_expired_sessions(sessions_data)

        # cache.set(cache_key, sessions_data, 60 * 60 * 24)  # Cache for 1 day
        cache.set(cache_key, sessions_data, 7200)  # Cache for 2 hours

    def clean_expired_sessions(self, sessions_data):
        valid_sessions = {}
        current_time = timezone.now()

        for session_key, session_info in sessions_data.items():
            try:
                if not Session.objects.filter(session_key=session_key).exists():
                    continue
                last_activity = timezone.datetime.fromisoformat(session_info['last_activity'])

                if timezone.is_naive(last_activity):
                    last_activity = timezone.make_aware(last_activity)

                if (current_time - last_activity).total_seconds() < 1800:  # 30 minutes
                    valid_sessions[session_key] = session_info
            except (ValueError, KeyError):
                continue

        return valid_sessions
    
    def check_session_limit(self, user_id, current_session_key):
        cache_key = f"{self.CACHE_PREFIX}{user_id}"
        sessions_data = cache.get(cache_key, {})

        active_sessions = [k for k in sessions_data.keys() if k != current_session_key]

        return len(active_sessions) >= self.MAX_SESSIONS_PER_USER
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip