"""
Utility to create in-app admin notifications and send email alerts.
"""
from django.core.mail import send_mail
from django.conf import settings


def notify_admin(notification_type, title, message, link=None):
    """Create an AdminNotification record and send email to admin addresses."""
    from counseling.models import AdminNotification
    AdminNotification.objects.create(
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )
    # Email notification
    try:
        send_mail(
            subject=f"[HRC] {title}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMIN_NOTIFICATION_EMAILS,
            fail_silently=True,
        )
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
