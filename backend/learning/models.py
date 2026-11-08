from django.db import models
from django.contrib.auth.models import User
from categories.models import Category

class LearningTopic(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_topics')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='learning_topics')
    target_hours = models.FloatField(default=50.0)
    logged_hours = models.FloatField(default=0.0)
    color = models.CharField(max_length=20, default='#38BDF8')
    icon = models.CharField(max_length=50, default='book')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.target_hours <= 0:
            return 100.0 if self.logged_hours > 0 else 0.0
        return min(100.0, round((self.logged_hours / self.target_hours) * 100, 1))

class LearningResource(models.Model):
    TYPE_CHOICES = [
        ('course', 'Course'),
        ('book', 'Book'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('practice', 'Practice / Project'),
        ('notes', 'Notes'),
    ]

    topic = models.ForeignKey(LearningTopic, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='course')
    url = models.URLField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic.title} - {self.title}"

class LearningMilestone(models.Model):
    topic = models.ForeignKey(LearningTopic, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    target_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_date', 'id']

    def __str__(self):
        return f"{self.topic.title} - {self.title}"

class StudySession(models.Model):
    SESSION_TYPE_CHOICES = [
        ('pomodoro', 'Pomodoro'),
        ('stopwatch', 'Stopwatch'),
        ('timer', 'Timer'),
        ('manual', 'Manual Log'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    topic = models.ForeignKey(LearningTopic, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_sessions')
    title = models.CharField(max_length=200, default='Study Session')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='pomodoro')
    duration_minutes = models.IntegerField(default=25)
    notes = models.TextField(blank=True, default='')
    rating = models.IntegerField(default=5, help_text="Rating 1-5")
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.duration_minutes}m)"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Automatically update topic's logged_hours if linked to topic and is_new
        if is_new and self.topic:
            added_hours = self.duration_minutes / 60.0
            self.topic.logged_hours = round(self.topic.logged_hours + added_hours, 2)
            self.topic.save(update_fields=['logged_hours', 'updated_at'])
