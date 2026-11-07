from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from schedules.models import Activity, ActivityCompletion
from tasks.models import Task
from learning.models import LearningProgress, StudySession


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):

    user = request.user
    today = timezone.localdate()

    activities = Activity.objects.filter(
        user=user,
        is_active=True,
        start_date__lte=today,
    ).filter(
        models_q_end_date(today)
    )

    completions = ActivityCompletion.objects.filter(
        user=user,
        date=today,
    )

    completed_ids = set(
        completions.filter(
            status=ActivityCompletion.Status.COMPLETED
        ).values_list("activity_id", flat=True)
    )

    pending_tasks = Task.objects.filter(
        user=user,
        status=Task.Status.PENDING
    ).count()

    completed_tasks = Task.objects.filter(
        user=user,
        status=Task.Status.COMPLETED
    ).count()

    sessions = StudySession.objects.filter(
        user=user,
        date=today,
    )

    study_minutes = sum(
        session.duration_minutes for session in sessions
    )

    total_activities = activities.count()
    completed_activities = len(completed_ids)

    progress = (
        round(completed_activities / total_activities * 100)
        if total_activities else 0
    )

    learning = LearningProgress.objects.filter(
        user=user,
        is_active=True,
    )

    return Response({
        "date": str(today),
        "statistics": {
            "total_activities": total_activities,
            "completed_activities": completed_activities,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "study_minutes": study_minutes,
            "daily_progress": progress,
        },
        "learning_progress": [
            {
                "title": item.title,
                "category": item.category,
                "level": item.level,
                "progress": item.progress_percentage,
            }
            for item in learning
        ],
    })


def models_q_end_date(date):
    from django.db.models import Q

    return Q(end_date__isnull=True) | Q(end_date__gte=date)