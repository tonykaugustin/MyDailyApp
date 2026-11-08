from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from categories.models import Category
from timetable.models import Activity, ActivityInstanceLog
from timetable.recurrence import get_occurrences_for_range, detect_conflicts
from tasks.models import Task, SubTask
from habits.models import Habit, HabitLog

class MyDailyCoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.cat = Category.objects.create(
            user=self.user, name="Deep Work", color="#7C6CFF", type="work"
        )

    def test_activity_recurrence_and_expansion(self):
        today = date.today()
        # Create a daily recurring activity
        act = Activity.objects.create(
            user=self.user,
            title="Daily Standup",
            category=self.cat,
            date=today,
            start_time=time(9, 0),
            end_time=time(9, 30),
            recurrence="daily"
        )
        # Check occurrences across 7 days
        next_week = today + timedelta(days=6)
        occs = get_occurrences_for_range(self.user, today, next_week)
        self.assertEqual(len(occs), 7)
        self.assertEqual(occs[0]['status'], 'pending')

        # Complete today's instance without modifying recurrence definition
        ActivityInstanceLog.objects.create(
            activity=act, user=self.user, date=today, status='completed'
        )
        occs_after = get_occurrences_for_range(self.user, today, next_week)
        self.assertEqual(occs_after[0]['status'], 'completed')
        self.assertEqual(occs_after[1]['status'], 'pending')

    def test_conflict_detection(self):
        today = date.today()
        Activity.objects.create(
            user=self.user,
            title="Design Review",
            category=self.cat,
            date=today,
            start_time=time(10, 0),
            end_time=time(11, 30),
            recurrence="none"
        )
        # Overlapping time 10:30 - 11:00
        conflicts = detect_conflicts(self.user, today, '10:30', '11:00')
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]['title'], 'Design Review')

        # Non-overlapping time 12:00 - 13:00
        no_conflicts = detect_conflicts(self.user, today, '12:00', '13:00')
        self.assertEqual(len(no_conflicts), 0)

    def test_habit_streaks(self):
        today = date.today()
        habit = Habit.objects.create(
            user=self.user,
            title="Daily Reading",
            category=self.cat,
            frequency="daily"
        )
        # Complete yesterday and today
        HabitLog.objects.create(habit=habit, user=self.user, date=today - timedelta(days=1), completed=True)
        HabitLog.objects.create(habit=habit, user=self.user, date=today, completed=True)
        habit.recalculate_streaks()

        self.assertEqual(habit.current_streak, 2)
        self.assertEqual(habit.best_streak, 2)
