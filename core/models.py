from django.db import models
from django.conf import settings

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200, default="Hope Reception Centre")
    tagline = models.CharField(max_length=255, default="Giving Hope to Children Since 2003")
    established_year = models.IntegerField(default=2003)
    address = models.TextField(default="Kijuguta ward, Northern division, Kabale municipality, Uganda")
    phone = models.CharField(max_length=50, default="+256 700 000 000")
    email = models.EmailField(default="info@hopereceptioncentre.org")
    mtn_mobile_money = models.CharField(max_length=50, default="+256 770 000 000 (Enid Origumusiriza)")
    airtel_money = models.CharField(max_length=50, default="+256 750 000 000 (Rev. Michael Asiimwe)")
    bank_details = models.TextField(default="Bank Name: Stanbic Bank Uganda\nAccount Name: Hope Reception Centre\nAccount No: 9030001234567\nBranch: Kabale Branch")
    about_text = models.TextField(default="Hope Reception Centre was started in 2003 in Kabale Municipality to provide shelter, care, counseling, and education to vulnerable children.")
    mission = models.TextField(default="To rehabilitate, empower, and restore hope to vulnerable and orphaned children through holistic care and counseling.")
    vision = models.TextField(default="A society where every child is nurtured, protected, and empowered to reach their full potential.")

    # Additional word-by-word UI text fields
    hero_title = models.CharField(max_length=250, default="Hope Reception Centre", help_text="Main heading on homepage hero banner")
    hero_subtext = models.CharField(max_length=300, default="Giving Hope to Vulnerable Children Since 2003", help_text="Subtitle under main heading")
    donate_button_text = models.CharField(max_length=100, default="Donate Now")
    anonymous_button_text = models.CharField(max_length=100, default="Get Anonymous Support")
    emergency_counseling_heading = models.CharField(max_length=200, default="Emergency Counseling")

    def __str__(self):
        return self.site_name

class CustomTextSnippet(models.Model):
    key = models.CharField(max_length=100, unique=True, help_text="Unique key identifier e.g. 'footer_disclaimer', 'homepage_welcome'")
    description = models.CharField(max_length=255, help_text="Description of where this text appears")
    content = models.TextField(help_text="Custom text content editable word-by-word")

    def __str__(self):
        return f"{self.key} ({self.description})"

class Director(models.Model):
    name = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='directors/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.title}"

class PageViewLog(models.Model):
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.path} at {self.timestamp}"
