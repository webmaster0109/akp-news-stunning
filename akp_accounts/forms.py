from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .models import AdminLoginAttempt

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip
class LimitedConcurrentSessionAdminAuthenticationForm(AuthenticationForm):

    def _log_attempt(self, username, status, failure_reason=None, user_object=None):
        AdminLoginAttempt.objects.create(
            username_attempt=username,
            user=user_object,
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:1024],
            status=status,
            failure_reason=failure_reason
        )
    def clean(self):
        username = self.cleaned_data.get('username')
        
        try:
            cleaned_data = super().clean()
            user = self.user_cache
        except forms.ValidationError as e:
            if username:
                self._log_attempt(username, 'FAILED_CREDENTIALS', failure_reason=str(e.messages[0]))
            raise e

        if user is not None:
            if not user.is_staff:
                failure_msg = "This account does not have staff privilages."
                self._log_attempt(
                    username, 'FAILED_NOT_STAFF', failure_reason=failure_msg, user_object=user
                )
                raise forms.ValidationError(
                    _(failure_msg),
                    code='not_staff',
                )
            
            active_session_count = 0
            all_sessions = Session.objects.filter(expire_date__gte=timezone.now())

            for session in all_sessions:
                session_data = session.get_decoded()
                if str(session_data.get('_auth_user_id')) == str(user.pk):
                    active_session_count += 1
            
            max_sessions = getattr(settings, 'MAX_CONCURRENT_ADMIN_SESSIONS', 10)

            if active_session_count > max_sessions:
                failure_msg = ("Login limit reached for this admin account. "
                               "A maximum of %(max_sessions)s concurrent session(s) is allowed. "
                               "Please log out from another active session or ensure other browser windows/tabs for the admin site are fully closed (sessions may take a few moments to clear after browser close).")
                self._log_attempt(username, 'FAILED_CONCURRENT_LIMIT', failure_reason=failure_msg % {'max_sessions': max_sessions}, user_object=user)
                raise forms.ValidationError(
                    _(failure_msg),
                    code='concurrent_session_limit',
                    params={'max_sessions': max_sessions},
                )
        return cleaned_data