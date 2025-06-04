from django.contrib import admin
from .models import CustomUser, AdminLoginAttempt, NewsletterSubscriber, NewsletterIssue
from .forms import LimitedConcurrentSessionAdminAuthenticationForm
from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

class LimitedAdminSite(AdminSite):
    login_form = LimitedConcurrentSessionAdminAuthenticationForm

limited_admin_site = LimitedAdminSite(name='limited_admin')
limited_admin_site.register(CustomUser)
limited_admin_site.register(AdminLoginAttempt)


class NewsLetterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('subscribed_at', 'is_active')
    search_fields = ('email',)
    actions = ['mark_active', 'mark_inactive']

    def mark_active(self, request, queryset):
        queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, 'Selected subscribers have been marked as active.', messages.SUCCESS)
    mark_active.short_description = "Mark selected subscribers as active"

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, 'Selected subscribers have been marked as inactive.', messages.SUCCESS)
    mark_inactive.short_description = "Mark selected subscribers as inactive"


limited_admin_site.register(NewsletterSubscriber, NewsLetterSubscriberAdmin)


def send_newsletter_action(modeladmin, request, queryset):
    for issue in queryset:
        if issue.is_sent:
            messages.warning(request, f"Newsletter '{issue.subject}' has already been sent.")
            continue

        active_subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        receipients_data = [{'email': sub.email, 'token': str(sub.unsubscribe_token)} for sub in active_subscribers]

        if not receipients_data:
            messages.info(request, f"No active subscribers to send '{issue.subject}'.")
            continue
        
        try:
            subject = issue.subject

            sent_count = 0
            for recipient in receipients_data:
                unsubscribe_url = request.build_absolute_uri(
                    reverse('unsubscribe_newsletter', kwargs={'token': recipient['token']})
                )
                context = {
                    'issue_subject': subject,
                    'unsubscribe_url': unsubscribe_url,
                    'issue_content_html': issue.content_html,
                }

                html_content = render_to_string('newsletter_email.html', context)
                text_content = render_to_string("newsletter_email.html", context)

                msg = EmailMultiAlternatives(
                    subject, 
                    text_content, 
                    "",
                    [recipient['email']]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
                sent_count += 1

            issue.is_sent = True
            issue.sent_at = timezone.now()
            issue.save()

            messages.success(request, f"Newsletter '{issue.subject}' sent to {sent_count} subscribers.")
        except Exception as e:
            messages.error(request, f"Error sending newsletter '{issue.subject}': {e}")
            continue


class NewsletterIssueAdmin(admin.ModelAdmin):
    list_display = ('subject', 'author', 'created_at', 'is_sent', 'sent_at')
    list_filter = ('is_sent', 'created_at', 'author')
    search_fields = ('subject', 'content_html', 'author__username')
    readonly_fields = ('sent_at',)
    actions = [send_newsletter_action]

    fieldsets = (
        (None, {
            "fields": (
                'subject',
                'author',
            ),
        }),
        ('Content (HTML recommended for rich formatting)', {
            "fields": (
                'content_html',
            ),
        }),
        ('Status', {
            "fields": (
                'is_sent',
                'sent_at',
            ),
        })
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        return super().save_model(request, obj, form, change)
    

limited_admin_site.register(NewsletterIssue, NewsletterIssueAdmin)