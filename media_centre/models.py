from django.db import models
from django.conf import settings
import json

class NewsArticle(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    featured_image = models.ImageField(upload_to='news/', blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    views_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class ArticleImage(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='news/gallery/')
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.article.title}"

class Video(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True, help_text="YouTube embed link or video URL")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True)
    is_live = models.BooleanField(default=False, help_text="Check if currently live streaming")
    is_recorded = models.BooleanField(default=True)
    requires_login = models.BooleanField(default=True, help_text="Must user log in to watch?")
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'[LIVE] ' if self.is_live else ''}{self.title}"

    class Meta:
        ordering = ['-created_at']

class VideoAttendance(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"

class UserStory(models.Model):
    title = models.CharField(max_length=200)
    author_alias = models.CharField(max_length=100, default="Anonymous")
    content = models.TextField()
    photo = models.ImageField(upload_to='stories/', blank=True, null=True)
    is_published = models.BooleanField(default=False, help_text="Requires admin approval to publish")
    has_user_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (by {self.author_alias})"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Stories'

# ─── Photo Gallery / Event Albums ───────────────────────────────────────────

class EventAlbum(models.Model):
    title = models.CharField(max_length=250, help_text="Name of the event or occasion")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    event_date = models.DateField(help_text="Date of the event")
    cover_photo = models.ImageField(upload_to='gallery/covers/', blank=True, null=True, help_text="Cover photo shown on gallery listing")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Event Album'
        verbose_name_plural = 'Event Albums'

    def photo_count(self):
        return self.photos.count()

class AlbumPhoto(models.Model):
    album = models.ForeignKey(EventAlbum, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='gallery/photos/')
    caption = models.CharField(max_length=300, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo in {self.album.title}"

    class Meta:
        ordering = ['order', 'uploaded_at']
        verbose_name = 'Album Photo'
        verbose_name_plural = 'Album Photos'


# ─── WebRTC Live Stream Signaling ────────────────────────────────────────────

class LiveStreamSignal(models.Model):
    """Stores WebRTC signaling data so admin can broadcast to viewers."""
    video = models.OneToOneField(Video, on_delete=models.CASCADE, related_name='stream_signal')
    is_broadcasting = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Signal for {self.video.title}"


class ViewerConnection(models.Model):
    """Each viewer's WebRTC offer, answer + ICE candidates for peer connection with admin."""
    signal = models.ForeignKey(LiveStreamSignal, on_delete=models.CASCADE, related_name='viewers')
    viewer_token = models.CharField(max_length=64)  # random token per viewer tab
    offer_sdp = models.TextField(blank=True, null=True)   # admin -> viewer
    answer_sdp = models.TextField(blank=True, null=True)  # viewer -> admin
    # ICE candidates stored as JSON arrays
    broadcaster_ice = models.TextField(default='[]')  # admin -> viewer
    viewer_ice = models.TextField(default='[]')       # viewer -> admin
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Viewer {self.viewer_token[:8]} on {self.signal.video.title}"
