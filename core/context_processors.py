from .models import SiteSetting, CustomTextSnippet
from counseling.models import AdminNotification


def site_settings(request):
    settings_obj = SiteSetting.objects.first()
    if not settings_obj:
        settings_obj = SiteSetting.objects.create()

    # Retrieve all custom text snippets into a dictionary
    snippets = {snippet.key: snippet.content for snippet in CustomTextSnippet.objects.all()}

    # Admin notification count for bell icon
    unread_notifications = 0
    notifications_list = []
    if request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'role', '') in ['super_admin', 'executive_director', 'director', 'counselor']):
        unread_notifications = AdminNotification.objects.filter(is_read=False).count()
        notifications_list = AdminNotification.objects.filter(is_read=False).order_by('-created_at')[:8]

    return {
        'site': settings_obj,
        'snippets': snippets,
        'unread_notifications': unread_notifications,
        'notifications_list': notifications_list,
    }
