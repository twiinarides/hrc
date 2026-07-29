from django.db import models
from django.conf import settings

class Program(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.CharField(max_length=300)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="fa-heart", help_text="FontAwesome icon class e.g. fa-hands-holding-child")
    image = models.ImageField(upload_to='programs/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']

class ProgramApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
    )
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='program_applications')
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=30)
    age = models.IntegerField(blank=True, null=True, help_text="Applicant's age")
    reason = models.TextField(help_text="Why are you applying for this program?")
    additional_info = models.TextField(blank=True, null=True, help_text="Any additional information you'd like to share")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal admin notes on this application")
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.program.title} ({self.status})"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Program Application'
        verbose_name_plural = 'Program Applications'
