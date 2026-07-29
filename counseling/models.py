from django.db import models
from django.conf import settings
import uuid

class CounselingSession(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    SESSION_TYPES = (
        ('in_person', 'In-Person at Centre'),
        ('digital_video', 'Digital Video Session'),
        ('digital_text', 'Digital Text Session'),
    )
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='counseling_sessions')
    counselor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_sessions')
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES, default='digital_video')
    preferred_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    meeting_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session for {self.client.username} on {self.preferred_date.strftime('%Y-%m-%d %H:%M')}"

class AnonymousSupportThread(models.Model):
    token = models.CharField(max_length=64, default=uuid.uuid4, unique=True)
    category = models.CharField(max_length=100, default='General Help')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Anonymous Thread {self.token[:8]} ({self.category})"

class AnonymousMessage(models.Model):
    thread = models.ForeignKey(AnonymousSupportThread, on_delete=models.CASCADE, related_name='messages')
    sender_is_counselor = models.BooleanField(default=False)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "Counselor" if self.sender_is_counselor else "User"
        return f"[{sender}] {self.content[:30]}..."
