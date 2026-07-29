from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import (
    NewsArticle, Video, UserStory, VideoAttendance,
    EventAlbum, AlbumPhoto, LiveStreamSignal, ViewerConnection
)
import json
import secrets


def news_list(request):
    articles = NewsArticle.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'media_centre/news_list.html', {'articles': articles})


def news_detail(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    article.views_count += 1
    article.save(update_fields=['views_count'])
    return render(request, 'media_centre/news_detail.html', {'article': article})


def video_list(request):
    videos = Video.objects.filter(is_recorded=True).order_by('-created_at')
    live_videos = Video.objects.filter(is_live=True)
    return render(request, 'media_centre/video_list.html', {
        'videos': videos,
        'live_videos': live_videos,
    })


def video_detail(request, slug):
    video = get_object_or_404(Video, slug=slug)

    # Require login to watch videos
    if video.requires_login and not request.user.is_authenticated:
        messages.warning(request, "Please log in or create a free account to watch videos and attend live sessions.")
        return redirect(f"/accounts/login/?next={request.path}")

    if request.user.is_authenticated:
        VideoAttendance.objects.get_or_create(video=video, user=request.user)

    video.views_count += 1
    video.save(update_fields=['views_count'])
    return render(request, 'media_centre/video_detail.html', {'video': video})


def submit_story(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        alias = request.POST.get('author_alias', 'Anonymous')
        content = request.POST.get('content')
        photo = request.FILES.get('photo')
        consent = request.POST.get('has_user_consent') == 'on'

        story = UserStory.objects.create(
            title=title,
            author_alias=alias,
            content=content,
            photo=photo,
            has_user_consent=consent,
            is_published=False  # Requires admin review
        )

        from core.notifications import notify_admin
        notify_admin(
            notification_type='story',
            title=f"New User Story Submitted: {title}",
            message=f"Title: {title}\nAuthor Alias: {alias}\nConsent Given: {consent}\nContent: {content}",
            link=f"/admin/media_centre/userstory/{story.id}/change/"
        )

        messages.success(request, "Thank you for sharing your story! Our team will review it before publishing.")
        return redirect('stories_list')

    return render(request, 'media_centre/submit_story.html')


def stories_list(request):
    stories = UserStory.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'media_centre/stories_list.html', {'stories': stories})


# ─── Photo Gallery / Event Albums ────────────────────────────────────────────

def album_list(request):
    albums = EventAlbum.objects.filter(is_published=True).order_by('-event_date')
    return render(request, 'media_centre/album_list.html', {'albums': albums})


def album_detail(request, slug):
    album = get_object_or_404(EventAlbum, slug=slug, is_published=True)
    photos = album.photos.all()
    return render(request, 'media_centre/album_detail.html', {
        'album': album,
        'photos': photos,
    })


# ─── WebRTC Live Streaming Signaling API ─────────────────────────────────────

@csrf_exempt
@require_POST
def rtc_broadcaster_offer(request, slug):
    """Admin posts their WebRTC SDP offer targeted at a specific viewer."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    video = get_object_or_404(Video, slug=slug)
    data = json.loads(request.body)
    
    # If no viewer_token, it's just the 'start broadcast' ping
    viewer_token = data.get('viewer_token')
    offer_sdp = data.get('offer')

    signal, _ = LiveStreamSignal.objects.get_or_create(video=video)
    
    if not viewer_token:
        # Just starting the broadcast
        signal.is_broadcasting = True
        signal.viewers.all().delete()
        signal.save()
        return JsonResponse({'status': 'broadcast_started'})
    
    # Offering to a specific viewer
    try:
        conn = signal.viewers.get(viewer_token=viewer_token)
        conn.offer_sdp = json.dumps(offer_sdp)
        conn.save(update_fields=['offer_sdp', 'updated_at'])
    except ViewerConnection.DoesNotExist:
        pass

    return JsonResponse({'status': 'offer_saved'})


@csrf_exempt
@require_POST
def rtc_broadcaster_ice(request, slug):
    """Admin sends an ICE candidate for a specific viewer."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    video = get_object_or_404(Video, slug=slug)
    data = json.loads(request.body)
    viewer_token = data.get('viewer_token')
    candidate = data.get('candidate')

    try:
        conn = video.stream_signal.viewers.get(viewer_token=viewer_token)
        existing = json.loads(conn.broadcaster_ice)
        existing.append(candidate)
        conn.broadcaster_ice = json.dumps(existing)
        conn.save(update_fields=['broadcaster_ice', 'updated_at'])
    except Exception:
        pass

    return JsonResponse({'status': 'ok'})


@csrf_exempt
@require_POST
def rtc_broadcaster_stop(request, slug):
    """Admin stops broadcasting."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    video = get_object_or_404(Video, slug=slug)
    try:
        signal = video.stream_signal
        signal.is_broadcasting = False
        signal.viewers.all().delete()
        signal.save()
    except LiveStreamSignal.DoesNotExist:
        pass

    return JsonResponse({'status': 'stopped'})


@require_GET
def rtc_poll_offer(request, slug):
    """Viewer polls to check if admin is broadcasting and gets THEIR specific SDP offer + Admin ICE."""
    video = get_object_or_404(Video, slug=slug)
    viewer_token = request.GET.get('viewer_token')
    
    if not viewer_token:
        return JsonResponse({'error': 'No viewer token'}, status=400)

    try:
        signal = video.stream_signal
        if not signal.is_broadcasting:
            return JsonResponse({'broadcasting': False})
            
        # Register viewer if they don't exist yet
        conn, created = ViewerConnection.objects.get_or_create(
            signal=signal,
            viewer_token=viewer_token,
            defaults={'broadcaster_ice': '[]', 'viewer_ice': '[]'}
        )
        
        return JsonResponse({
            'broadcasting': True,
            'offer': json.loads(conn.offer_sdp) if conn.offer_sdp else None,
            'broadcaster_ice': json.loads(conn.broadcaster_ice)
        })
    except LiveStreamSignal.DoesNotExist:
        pass

    return JsonResponse({'broadcasting': False})


@csrf_exempt
@require_POST
def rtc_viewer_join(request, slug):
    """(Deprecated) Handled implicitly by rtc_poll_offer now."""
    return JsonResponse({'status': 'ok'})


@csrf_exempt
@require_POST
def rtc_viewer_answer(request, slug):
    """Viewer posts their SDP answer back to the admin."""
    video = get_object_or_404(Video, slug=slug)
    data = json.loads(request.body)
    viewer_token = data.get('viewer_token')
    answer = data.get('answer')

    try:
        conn = video.stream_signal.viewers.get(viewer_token=viewer_token)
        conn.answer_sdp = json.dumps(answer)
        conn.save(update_fields=['answer_sdp', 'updated_at'])
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

    return JsonResponse({'status': 'answer_saved'})


@csrf_exempt
@require_POST
def rtc_viewer_ice(request, slug):
    """Viewer sends ICE candidates to admin."""
    video = get_object_or_404(Video, slug=slug)
    data = json.loads(request.body)
    viewer_token = data.get('viewer_token')
    candidate = data.get('candidate')

    try:
        conn = video.stream_signal.viewers.get(viewer_token=viewer_token)
        existing = json.loads(conn.viewer_ice)
        existing.append(candidate)
        conn.viewer_ice = json.dumps(existing)
        conn.save(update_fields=['viewer_ice', 'updated_at'])
    except Exception:
        pass

    return JsonResponse({'status': 'ok'})


@require_GET
def rtc_broadcaster_poll_viewers(request, slug):
    """Admin polls for new viewers (to create offers) + viewer answers/ICE."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    video = get_object_or_404(Video, slug=slug)
    try:
        signal = video.stream_signal
        viewers = []
        for conn in signal.viewers.all():
            viewers.append({
                'viewer_token': conn.viewer_token,
                'needs_offer': not bool(conn.offer_sdp),
                'answer': json.loads(conn.answer_sdp) if conn.answer_sdp else None,
                'ice_candidates': json.loads(conn.viewer_ice),
            })
        return JsonResponse({'viewers': viewers})
    except LiveStreamSignal.DoesNotExist:
        return JsonResponse({'viewers': []})
