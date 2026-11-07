from django.conf import settings
from django.db import models


class LearningProgress(models.Model):

    class Category(models.TextChoices):
        GERMAN = "german", "German"
        AUTOMOTIVE = "automotive", "Automotive"

    class Level(models.TextChoices):
        A1 = "A1", "A1"
        A2 = "A2", "A2"
        B1 = "B1", "B1"
        B2 = "B2", "B2"
        FUNDAMENTALS = "fundamentals", "Fundamentals"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_progress"
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices
    )

    level = models.CharField(
        max_length=20,
        choices=Level.choices
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    total_lessons = models.PositiveIntegerField(default=0)

    completed_lessons = models.PositiveIntegerField(default=0)

    progress_percentage = models.PositiveSmallIntegerField(
        default=0
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "level"]

    def save(self, *args, **kwargs):
        if self.total_lessons:
            self.progress_percentage = min(
                100,
                round(
                    self.completed_lessons
                    / self.total_lessons * 100
                )
            )
        else:
            self.progress_percentage = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class StudySession(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_sessions"
    )

    learning_progress = models.ForeignKey(
        LearningProgress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_sessions"
    )

    title = models.CharField(max_length=200)

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    duration_minutes = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            start = (
                self.start_time.hour * 60
                + self.start_time.minute
            )

            end = (
                self.end_time.hour * 60
                + self.end_time.minute
            )

            self.duration_minutes = max(0, end - start)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title