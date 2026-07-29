from django.db import models
from django.conf import settings
import random
import string
import uuid


def generate_short_token():
    """Generate a 6-character uppercase alphanumeric token like HRC-AB3"""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=6))
    return f"HRC-{code}"


class CounselingSession(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    SESSION_TYPES = (
        ('individual', 'Individual Session'),
        ('group', 'Group Session'),
        ('digital', 'Digital / Online Session'),
        ('family', 'Family Session'),
        ('in_person', 'In-Person at Centre'),
        ('digital_video', 'Digital Video Session'),
        ('digital_text', 'Digital Text Session'),
    )
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='counseling_sessions')
    counselor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_sessions')
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES, default='individual')
    preferred_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    meeting_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session for {self.client.username} on {self.preferred_date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


class AnonymousSupportThread(models.Model):
    # Short, human-readable token like HRC-AB3K7P
    token = models.CharField(max_length=20, default=generate_short_token, unique=True)
    category = models.CharField(max_length=100, default='General Help')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Anonymous Thread {self.token} ({self.category})"

    class Meta:
        ordering = ['-created_at']


class AnonymousMessage(models.Model):
    thread = models.ForeignKey(AnonymousSupportThread, on_delete=models.CASCADE, related_name='messages')
    sender_is_counselor = models.BooleanField(default=False)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "Counselor" if self.sender_is_counselor else "User"
        return f"[{sender}] {self.content[:30]}..."

    class Meta:
        ordering = ['timestamp']


# ─── Admin Notification System ────────────────────────────────────────────────

class AdminNotification(models.Model):
    TYPE_CHOICES = (
        ('session', 'Counseling Session'),
        ('application', 'Program Application'),
        ('anonymous', 'Anonymous Message'),
        ('donation', 'Donation'),
        ('story', 'User Story'),
        ('contact', 'Contact Form'),
        ('live', 'Live Stream'),
        ('general', 'General'),
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True, help_text="Admin URL to view this item")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.notification_type}] {self.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admin Notification'
        verbose_name_plural = 'Admin Notifications'
