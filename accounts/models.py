from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('executive_director', 'Executive Director'),
        ('director', 'Director'),
        ('treasurer', 'Treasurer'),
        ('counselor', 'Counselor'),
        ('social_worker', 'Social Worker'),
        ('client', 'Client'),
        ('volunteer', 'Volunteer'),
        ('donor', 'Donor'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
