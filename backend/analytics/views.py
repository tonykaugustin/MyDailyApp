from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from datetime import date, datetime, timedelta
from django.db.models import Sum, Count, Q
from timetable.models import Activity, ActivityInstanceLog
from timetable.recurrence import get_occurrences_for_range
from tasks.models import Task
from learning.models import LearningTopic, StudySession
from habits.models import Habit, HabitLog
from goals.models import Goal
from notifications.models import Notification
from tasks.serializers import TaskSerializer
from goals.serializers import GoalSerializer
from learning.serializers import LearningTopicSerializer, StudySessionSerializer
from habits.serializers import HabitSerializer

class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

        # 1. Activities today
        today_occurrences = get_occurrences_for_range(user, today, today)
        total_activities = len(today_occurrences)
        completed_activities = sum(1 for o in today_occurrences if o['status'] == 'completed')
        pending_activities = sum(1 for o in today_occurrences if o['status'] == 'pending')

        # 2. Tasks today & pending
        tasks_qs = Task.objects.filter(user=user, is_archived=False)
        today_tasks_qs = tasks_qs.filter(due_date=today)
        completed_tasks_today = today_tasks_qs.filter(status='completed').count()
        pending_tasks_today = today_tasks_qs.exclude(status='completed').count()
        total_pending_tasks = tasks_qs.exclude(status='completed').count()

        # 3. Total study time today
        study_sessions_today = StudySession.objects.filter(user=user, created_at__date=today)
        total_study_minutes = study_sessions_today.aggregate(total=Sum('duration_minutes'))['total'] or 0
        total_study_hours = round(total_study_minutes / 60.0, 1)

        # 4. Daily completion percentage
        total_items_today = total_activities + today_tasks_qs.count()
        completed_items_today = completed_activities + completed_tasks_today
        if total_items_today > 0:
            daily_completion_percentage = round((completed_items_today / total_items_today) * 100, 1)
        else:
            daily_completion_percentage = 0.0

        # 5. Active goals count
        active_goals_qs = Goal.objects.filter(user=user, status='in_progress')
        active_goals_count = active_goals_qs.count()

        # 6. Additional sections data
        # Today's tasks (up to 8)
        displayed_tasks = tasks_qs.filter(
            Q(due_date=today) | Q(priority='urgent') | Q(status='in_progress')
        )[:8]

        # Active goals (top 4)
        displayed_goals = active_goals_qs[:4]

        # Learning progress (top 4 active topics)
        learning_topics = LearningTopic.objects.filter(user=user, status='active')[:4]

        # Habits today
        habits = Habit.objects.filter(user=user, is_active=True)

        # Recent activities (last 5 completed/logged items)
        recent_study = StudySession.objects.filter(user=user).order_by('-created_at')[:3]
        recent_tasks = Task.objects.filter(user=user, status='completed').order_by('-completed_at')[:3]

        # Upcoming reminders (activities starting soon today)
        upcoming_reminders = []
        for occ in today_occurrences:
            if occ['status'] == 'pending':
                upcoming_reminders.append({
                    'id': occ['activity_id'],
                    'title': occ['title'],
                    'time': occ['start_time'],
                    'category': occ['category']['name'] if occ['category'] else None,
                    'color': occ['color'],
                    'reminder_minutes': occ['reminder_minutes']
                })

        # Weekly productivity summary (past 7 days)
        weekly_summary = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_occurrences = get_occurrences_for_range(user, day, day)
            day_act_total = len(day_occurrences)
            day_act_completed = sum(1 for o in day_occurrences if o['status'] == 'completed')

            day_tasks_completed = Task.objects.filter(
                user=user,
                completed_at__date=day
            ).count()

            day_study = StudySession.objects.filter(
                user=user,
                created_at__date=day
            ).aggregate(total=Sum('duration_minutes'))['total'] or 0

            day_habits = HabitLog.objects.filter(
                user=user,
                date=day,
                completed=True
            ).count()

            weekly_summary.append({
                'date': day.strftime('%Y-%m-%d'),
                'day_name': day.strftime('%a'),
                'activities_completed': day_act_completed,
                'activities_total': day_act_total,
                'tasks_completed': day_tasks_completed,
                'study_minutes': day_study,
                'habits_completed': day_habits,
            })

        return Response({
            'stats': {
                'total_activities_today': total_activities,
                'completed_activities_today': completed_activities,
                'pending_activities_today': pending_activities,
                'pending_tasks_today': pending_tasks_today,
                'total_pending_tasks': total_pending_tasks,
                'completed_tasks_today': completed_tasks_today,
                'total_study_minutes_today': total_study_minutes,
                'total_study_hours_today': total_study_hours,
                'daily_completion_percentage': daily_completion_percentage,
                'active_goals_count': active_goals_count,
            },
            'today_schedule': today_occurrences,
            'today_tasks': TaskSerializer(displayed_tasks, many=True).data,
            'active_goals': GoalSerializer(displayed_goals, many=True).data,
            'learning_progress': LearningTopicSerializer(learning_topics, many=True).data,
            'habits': HabitSerializer(habits, many=True).data,
            'upcoming_reminders': upcoming_reminders[:6],
            'recent_study_sessions': StudySessionSerializer(recent_study, many=True).data,
            'weekly_summary': weekly_summary,
        })

class AnalyticsOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()
        # Monthly and 30-day productivity trends
        days_30 = [today - timedelta(days=i) for i in range(29, -1, -1)]

        study_by_day = list(
            StudySession.objects.filter(user=user, created_at__date__gte=days_30[0])
            .values('created_at__date')
            .annotate(total_minutes=Sum('duration_minutes'))
        )
        study_map = {item['created_at__date'].strftime('%Y-%m-%d'): item['total_minutes'] for item in study_by_day}

        # Categories distribution
        categories_data = []
        from categories.models import Category
        for cat in Category.objects.filter(user=user):
            act_count = Activity.objects.filter(user=user, category=cat).count()
            task_count = Task.objects.filter(user=user, category=cat).count()
            study_min = StudySession.objects.filter(user=user, category=cat).aggregate(total=Sum('duration_minutes'))['total'] or 0
            categories_data.append({
                'id': cat.id,
                'name': cat.name,
                'color': cat.color,
                'activities_count': act_count,
                'tasks_count': task_count,
                'study_minutes': study_min
            })

        return Response({
            'study_30_days': [
                {'date': d.strftime('%Y-%m-%d'), 'minutes': study_map.get(d.strftime('%Y-%m-%d'), 0)}
                for d in days_30
            ],
            'category_distribution': categories_data,
            'total_goals': Goal.objects.filter(user=user).count(),
            'achieved_goals': Goal.objects.filter(user=user, status='achieved').count(),
            'total_tasks_completed': Task.objects.filter(user=user, status='completed').count(),
            'active_habits_count': Habit.objects.filter(user=user, is_active=True).count(),
        })
