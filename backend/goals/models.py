from django.db import models
from django.contrib.auth.models import User
from categories.models import Category

class Goal(models.Model):
    TIMEFRAME_CHOICES = [
        ('short_term', 'Short-term (< 3 months)'),
        ('medium_term', 'Medium-term (3-12 months)'),
        ('long_term', 'Long-term (1+ year)'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('abandoned', 'Abandoned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals')
    timeframe = models.CharField(max_length=20, choices=TIMEFRAME_CHOICES, default='short_term')
    target_date = models.DateField(null=True, blank=True)
    target_value = models.FloatField(default=100.0)
    current_value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=30, default='%')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['target_date', '-created_at']

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.target_value <= 0:
            return 100.0 if self.current_value >= 0 else 0.0
        return min(100.0, max(0.0, round((self.current_value / self.target_value) * 100, 1)))

class GoalMilestone(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    target_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_date', 'id']

    def __str__(self):
        return f"{self.goal.title} - {self.title}"
