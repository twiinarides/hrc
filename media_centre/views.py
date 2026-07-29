from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NewsArticle, Video, UserStory, VideoAttendance, EventAlbum, AlbumPhoto


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
