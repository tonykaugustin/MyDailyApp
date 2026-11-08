from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, datetime
from .models import Habit, HabitLog
from .serializers import HabitSerializer, HabitLogSerializer

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Habit.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        time_of_day = self.request.query_params.get('time_of_day')
        is_active = self.request.query_params.get('is_active')

        if category:
            qs = qs.filter(category_id=category)
        if time_of_day:
            qs = qs.filter(time_of_day=time_of_day)
        if is_active is not None:
            qs = qs.filter(is_active=(is_active.lower() == 'true'))

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle')
    def toggle_day(self, request, pk=None):
        habit = self.get_object()
        date_str = request.data.get('date', date.today().strftime('%Y-%m-%d'))
        notes = request.data.get('notes', '')

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = date.today()

        log = HabitLog.objects.filter(habit=habit, date=target_date).first()

        if log:
            if log.completed:
                log.delete()
                completed = False
            else:
                log.completed = True
                log.save()
                completed = True
        else:
            HabitLog.objects.create(
                habit=habit,
                user=request.user,
                date=target_date,
                completed=True,
                notes=notes
            )
            completed = True

        habit.recalculate_streaks()

        return Response({
            'habit_id': habit.id,
            'date': target_date.strftime('%Y-%m-%d'),
            'completed': completed,
            'current_streak': habit.current_streak,
            'best_streak': habit.best_streak,
        })
