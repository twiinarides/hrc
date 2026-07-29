from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Director, SiteSetting, PageViewLog
from programs.models import Program, ProgramApplication
from media_centre.models import NewsArticle, Video, UserStory, EventAlbum
from donations.models import Donation
from counseling.models import CounselingSession, AnonymousSupportThread
from accounts.models import User


def home_view(request):
    # Log page view
    PageViewLog.objects.create(
        path=request.path,
        ip_address=request.META.get('REMOTE_ADDR'),
        user=request.user if request.user.is_authenticated else None
    )
    programs = Program.objects.filter(is_active=True)[:3]
    news = NewsArticle.objects.filter(is_published=True).order_by('-created_at')[:3]
    videos = Video.objects.order_by('-created_at')[:3]
    stories = UserStory.objects.filter(is_published=True).order_by('-created_at')[:3]
    directors = Director.objects.all()
    albums = EventAlbum.objects.filter(is_published=True).order_by('-event_date')[:3]

    context = {
        'programs': programs,
        'news': news,
        'videos': videos,
        'stories': stories,
        'directors': directors,
        'albums': albums,
    }
    return render(request, 'core/home.html', context)


def about_view(request):
    directors = Director.objects.all()
    return render(request, 'core/about.html', {'directors': directors})


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email_from = request.POST.get('email', '')
        subject_in = request.POST.get('subject', 'Contact Form Message')
        message_in = request.POST.get('message', '')

        from core.notifications import notify_admin
        notify_admin(
            notification_type='contact',
            title=f"Contact Message: {subject_in} (from {name})",
            message=f"Name: {name}\nEmail: {email_from}\n\nMessage:\n{message_in}",
            link="/admin/"
        )

        return render(request, 'core/contact.html', {'submitted': True})
    return render(request, 'core/contact.html')


def _require_admin(request):
    """Return True if user has admin-level access."""
    if not request.user.is_authenticated:
        return False
    return request.user.is_staff or request.user.role in [
        'super_admin', 'executive_director', 'director', 'treasurer', 'counselor'
    ]


@login_required
def admin_stats_dashboard(request):
    if not _require_admin(request):
        messages.error(request, "You do not have permission to access the Admin Dashboard.")
        return redirect('home')

    # ── KPI Counts ──────────────────────────────────────────────────────────
    total_visitors = PageViewLog.objects.count()
    total_users = User.objects.count()
    total_donations = Donation.objects.count()
    total_sessions = CounselingSession.objects.count()
    total_stories = UserStory.objects.count()
    total_videos = Video.objects.count()
    total_programs = Program.objects.count()
    total_articles = NewsArticle.objects.count()
    total_applications = ProgramApplication.objects.count()
    total_albums = EventAlbum.objects.count()
    pending_sessions = CounselingSession.objects.filter(status='pending').count()
    pending_stories = UserStory.objects.filter(is_published=False).count()
    pending_applications = ProgramApplication.objects.filter(status='pending').count()

    # ── Recent Data ──────────────────────────────────────────────────────────
    recent_views = PageViewLog.objects.order_by('-timestamp')[:30]
    recent_users = User.objects.order_by('-date_joined')[:10]
    recent_sessions = CounselingSession.objects.order_by('-created_at')[:10]
    recent_applications = ProgramApplication.objects.order_by('-submitted_at')[:10]
    pending_story_list = UserStory.objects.filter(is_published=False).order_by('-created_at')[:8]
    recent_donations = Donation.objects.order_by('-created_at')[:10]
    recent_articles = NewsArticle.objects.order_by('-created_at')[:8]
    all_programs = Program.objects.all()
    all_videos = Video.objects.order_by('-created_at')[:10]
    all_albums = EventAlbum.objects.order_by('-event_date')[:10]
    anonymous_threads = AnonymousSupportThread.objects.filter(is_active=True).order_by('-created_at')[:10]

    context = {
        # KPIs
        'total_visitors': total_visitors,
        'total_users': total_users,
        'total_donations': total_donations,
        'total_sessions': total_sessions,
        'total_stories': total_stories,
        'total_videos': total_videos,
        'total_programs': total_programs,
        'total_articles': total_articles,
        'total_applications': total_applications,
        'total_albums': total_albums,
        'pending_sessions': pending_sessions,
        'pending_stories': pending_stories,
        'pending_applications': pending_applications,
        # Lists
        'recent_views': recent_views,
        'recent_users': recent_users,
        'recent_sessions': recent_sessions,
        'recent_applications': recent_applications,
        'pending_story_list': pending_story_list,
        'recent_donations': recent_donations,
        'recent_articles': recent_articles,
        'all_programs': all_programs,
        'all_videos': all_videos,
        'all_albums': all_albums,
        'anonymous_threads': anonymous_threads,
    }
    return render(request, 'core/admin_dashboard.html', context)


# ─── Admin Action Endpoints ───────────────────────────────────────────────────

@login_required
def approve_story(request, pk):
    if not _require_admin(request):
        return redirect('home')
    story = get_object_or_404(UserStory, pk=pk)
    story.is_published = True
    story.save()
    messages.success(request, f"Story '{story.title}' has been approved and published.")
    return redirect('admin_stats_dashboard')


@login_required
def reject_story(request, pk):
    if not _require_admin(request):
        return redirect('home')
    story = get_object_or_404(UserStory, pk=pk)
    story.delete()
    messages.warning(request, "Story has been rejected and removed.")
    return redirect('admin_stats_dashboard')


@login_required
def approve_session(request, pk):
    if not _require_admin(request):
        return redirect('home')
    session = get_object_or_404(CounselingSession, pk=pk)
    session.status = 'approved'
    session.save()
    # Notify client
    try:
        send_mail(
            subject="[HRC] Your Counseling Session Has Been Approved",
            message=f"Dear {session.client.username},\n\nYour counseling session request for {session.preferred_date.strftime('%d %B %Y at %H:%M')} has been approved.\n\nIf this is a digital session, a meeting link will be sent separately.\n\nThank you,\nHope Reception Centre Team.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMIN_NOTIFICATION_EMAILS,
            fail_silently=True,
        )
    except Exception:
        pass
    messages.success(request, f"Session for {session.client.username} has been approved.")
    return redirect('admin_stats_dashboard')


@login_required
def verify_donation(request, pk):
    if not _require_admin(request):
        return redirect('home')
    donation = get_object_or_404(Donation, pk=pk)
    donation.is_verified = True
    donation.save()
    messages.success(request, f"Donation of {donation.amount} from {donation.donor_name} verified.")
    return redirect('admin_stats_dashboard')


from django.http import JsonResponse
from counseling.models import AdminNotification

def api_unread_notifications(request):
    if not request.user.is_authenticated or not (request.user.is_staff or getattr(request.user, 'role', '') in ['super_admin', 'executive_director', 'director', 'counselor']):
        return JsonResponse({'count': 0, 'latest': []})

    unread = AdminNotification.objects.filter(is_read=False)
    count = unread.count()
    latest_items = list(unread.order_by('-created_at')[:5].values('id', 'title', 'notification_type', 'message', 'created_at', 'link'))
    
    for item in latest_items:
        item['created_at'] = item['created_at'].strftime('%H:%M')

    return JsonResponse({
        'count': count,
        'latest': latest_items
    })

