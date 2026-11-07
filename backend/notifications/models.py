from django.conf import settings
from django.db import models


class NotificationPreference(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences"
    )

    enabled = models.BooleanField(default=True)

    push_enabled = models.BooleanField(default=True)

    local_enabled = models.BooleanField(default=True)

    default_reminder_minutes = models.PositiveIntegerField(
        default=10
    )

    morning_summary_enabled = models.BooleanField(default=True)

    morning_summary_time = models.TimeField(
        default="06:00"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification settings - {self.user}"