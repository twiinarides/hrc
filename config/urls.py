from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from accounts import views as accounts_views
from programs import views as program_views
from counseling import views as counseling_views
from donations import views as donation_views
from media_centre import views as media_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core
    path('', core_views.home_view, name='home'),
    path('about/', core_views.about_view, name='about'),
    path('contact/', core_views.contact_view, name='contact'),
    path('dashboard/stats/', core_views.admin_stats_dashboard, name='admin_stats_dashboard'),
    path('dashboard/approve-story/<int:pk>/', core_views.approve_story, name='approve_story'),
    path('dashboard/reject-story/<int:pk>/', core_views.reject_story, name='reject_story'),
    path('dashboard/approve-session/<int:pk>/', core_views.approve_session, name='approve_session'),
    path('dashboard/verify-donation/<int:pk>/', core_views.verify_donation, name='verify_donation'),
    path('api/notifications/unread/', core_views.api_unread_notifications, name='api_unread_notifications'),

    # Accounts (custom)
    path('accounts/register/', accounts_views.register_view, name='register'),
    path('accounts/login/', accounts_views.login_view, name='login'),
    path('accounts/logout/', accounts_views.logout_view, name='logout'),
    path('accounts/profile/', accounts_views.profile_view, name='profile'),

    # Django-allauth (Google login etc.) — must come AFTER custom account paths
    path('accounts/', include('allauth.urls')),

    # Programs
    path('programs/', program_views.program_list, name='program_list'),
    path('programs/<slug:slug>/', program_views.program_detail, name='program_detail'),
    path('programs/<slug:slug>/apply/', program_views.apply_program, name='apply_program'),
    path('my-applications/', program_views.my_applications, name='my_applications'),

    # Counseling
    path('counseling/book/', counseling_views.book_session, name='book_session'),
    path('counseling/my-sessions/', counseling_views.my_sessions, name='my_sessions'),
    path('counseling/anonymous/', counseling_views.anonymous_chat, name='anonymous_chat'),

    # Donations
    path('donate/', donation_views.donate_view, name='donate'),

    # Media Centre
    path('news/', media_views.news_list, name='news_list'),
    path('news/<slug:slug>/', media_views.news_detail, name='news_detail'),
    path('videos/', media_views.video_list, name='video_list'),
    path('videos/<slug:slug>/', media_views.video_detail, name='video_detail'),
    path('stories/', media_views.stories_list, name='stories_list'),
    path('stories/share/', media_views.submit_story, name='submit_story'),

    # Photo Gallery / Albums
    path('gallery/', media_views.album_list, name='album_list'),
    path('gallery/<slug:slug>/', media_views.album_detail, name='album_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
