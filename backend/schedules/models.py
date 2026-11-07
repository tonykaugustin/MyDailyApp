from django.conf import settings
from django.db import models


class Activity(models.Model):

    class Category(models.TextChoices):
        GERMAN = "german", "German"
        AUTOMOTIVE = "automotive", "Automotive"
        PERSONAL = "personal", "Personal"
        HEALTH = "health", "Health"
        OTHER = "other", "Other"

    class Recurrence(models.TextChoices):
        NONE = "none", "Does not repeat"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.PERSONAL
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    recurrence = models.CharField(
        max_length=20,
        choices=Recurrence.choices,
        default=Recurrence.NONE
    )

    weekdays = models.JSONField(default=list, blank=True)

    reminder_minutes = models.PositiveIntegerField(
        default=10
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["user", "start_date"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return self.title


class ActivityCompletion(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="completions"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_completions"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(
                fields=["activity", "date"],
                name="unique_activity_completion_per_day"
            )
        ]

    def __str__(self):
        return f"{self.activity.title} - {self.date}"