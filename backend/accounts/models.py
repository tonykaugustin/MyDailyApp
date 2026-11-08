from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    THEME_CHOICES = [
        ('dark', 'Dark Theme'),
        ('light', 'Light Theme'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=150, blank=True)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='dark')
    avatar = models.CharField(max_length=255, blank=True, default='')
    daily_study_goal_hours = models.FloatField(default=2.0)
    week_start_day = models.IntegerField(default=0)  # 0 = Monday, 6 = Sunday
    dashboard_layout = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            display_name=instance.get_full_name() or instance.username
        )
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
