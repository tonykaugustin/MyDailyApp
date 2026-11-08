from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
from datetime import date, timedelta

class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Every day'),
        ('weekdays', 'Weekdays only'),
        ('weekends', 'Weekends only'),
        ('custom', 'Custom days'),
    ]

    TIME_OF_DAY_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('anytime', 'Anytime'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='habits')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    target_days_per_week = models.IntegerField(default=7)
    time_of_day = models.CharField(max_length=20, choices=TIME_OF_DAY_CHOICES, default='anytime')
    color = models.CharField(max_length=20, default='#22C55E')
    icon = models.CharField(max_length=50, default='check-circle')
    current_streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['time_of_day', '-created_at']

    def __str__(self):
        return self.title

    def recalculate_streaks(self):
        """
        Calculates the consecutive streak ending at today or yesterday.
        """
        logs = set(
            HabitLog.objects.filter(habit=self, completed=True)
            .values_list('date', flat=True)
        )
        if not logs:
            self.current_streak = 0
            self.save(update_fields=['current_streak'])
            return

        today = date.today()
        # Check current streak
        streak = 0
        check_date = today
        if check_date not in logs:
            check_date = today - timedelta(days=1)

        while check_date in logs:
            streak += 1
            check_date -= timedelta(days=1)

        self.current_streak = streak
        if streak > self.best_streak:
            self.best_streak = streak

        self.save(update_fields=['current_streak', 'best_streak'])

class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habit_logs')
    date = models.DateField()
    completed = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['habit', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.title} on {self.date}: {self.completed}"
