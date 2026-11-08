from django.db import models
from django.contrib.auth.models import User
from categories.models import Category

class Activity(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'Does not repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('selected_weekdays', 'Selected weekdays'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom recurrence'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    date = models.DateField(help_text="Start date or specific date of the activity")
    start_time = models.TimeField()
    end_time = models.TimeField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    reminder_minutes = models.IntegerField(default=15, help_text="Reminder minutes before activity start")
    recurrence = models.CharField(max_length=30, choices=RECURRENCE_CHOICES, default='none')
    selected_weekdays = models.JSONField(default=list, blank=True, help_text="List of weekday integers (0=Mon, 6=Sun)")
    end_date = models.DateField(null=True, blank=True, help_text="Optional recurrence end date")
    color = models.CharField(max_length=20, default='#7C6CFF')
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False, help_text="Status for non-recurring activities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} ({self.date} {self.start_time}-{self.end_time})"

class ActivityInstanceLog(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('rescheduled', 'Rescheduled'),
    ]

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='instance_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    date = models.DateField(help_text="The occurrence date this log applies to")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    rescheduled_date = models.DateField(null=True, blank=True)
    rescheduled_start_time = models.TimeField(null=True, blank=True)
    rescheduled_end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['activity', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.activity.title} on {self.date}: {self.status}"
