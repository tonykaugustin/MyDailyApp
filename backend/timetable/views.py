from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, datetime, timedelta
from .models import Activity, ActivityInstanceLog
from .serializers import ActivitySerializer, ActivityInstanceLogSerializer
from .recurrence import get_occurrences_for_range, detect_conflicts

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Activity.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        priority = self.request.query_params.get('priority')
        is_active = self.request.query_params.get('is_active')

        if category:
            qs = qs.filter(category_id=category)
        if priority:
            qs = qs.filter(priority=priority)
        if is_active is not None:
            qs = qs.filter(is_active=(is_active.lower() == 'true'))

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='occurrences')
    def occurrences(self, request):
        """
        Returns expanded occurrences for any date range: Daily, Weekly, Monthly, Agenda.
        Query params: start_date=YYYY-MM-DD, end_date=YYYY-MM-DD
        """
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        today = date.today()
        if not start_date_str:
            start_date = today
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today

        if not end_date_str:
            end_date = start_date + timedelta(days=7)
        else:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = start_date + timedelta(days=7)

        category_id = request.query_params.get('category')
        priority = request.query_params.get('priority')

        occurrences = get_occurrences_for_range(
            user=request.user,
            range_start=start_date,
            range_end=end_date,
            category_id=category_id,
            priority=priority
        )
        return Response(occurrences)

    @action(detail=False, methods=['get'], url_path='today')
    def today_schedule(self, request):
        """
        Returns today's occurrences.
        """
        today = date.today()
        occurrences = get_occurrences_for_range(
            user=request.user,
            range_start=today,
            range_end=today
        )
        return Response(occurrences)

    @action(detail=False, methods=['post'], url_path='detect-conflicts')
    def check_conflicts(self, request):
        """
        Detects if an activity overlaps with any existing activities on a date.
        """
        check_date = request.data.get('date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        exclude_id = request.data.get('exclude_activity_id')

        if not (check_date and start_time and end_time):
            return Response(
                {"error": "date, start_time, and end_time are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conflicts = detect_conflicts(
                user=request.user,
                check_date=check_date,
                start_time=start_time,
                end_time=end_time,
                exclude_activity_id=exclude_id
            )
            return Response({"has_conflicts": len(conflicts) > 0, "conflicts": conflicts})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='complete')
    def mark_complete(self, request, pk=None):
        activity = self.get_object()
        occ_date_str = request.data.get('date', date.today().strftime('%Y-%m-%d'))
        notes = request.data.get('notes', '')

        try:
            occ_date = datetime.strptime(occ_date_str, '%Y-%m-%d').date()
        except ValueError:
            occ_date = date.today()

        if activity.recurrence == 'none':
            activity.is_completed = True
            activity.save(update_fields=['is_completed', 'updated_at'])

        log, _ = ActivityInstanceLog.objects.update_or_create(
            activity=activity,
            user=request.user,
            date=occ_date,
            defaults={'status': 'completed', 'notes': notes}
        )
        return Response({'status': 'completed', 'date': occ_date.strftime('%Y-%m-%d')})

    @action(detail=True, methods=['post'], url_path='uncomplete')
    def mark_uncomplete(self, request, pk=None):
        activity = self.get_object()
        occ_date_str = request.data.get('date', date.today().strftime('%Y-%m-%d'))

        try:
            occ_date = datetime.strptime(occ_date_str, '%Y-%m-%d').date()
        except ValueError:
            occ_date = date.today()

        if activity.recurrence == 'none':
            activity.is_completed = False
            activity.save(update_fields=['is_completed', 'updated_at'])

        ActivityInstanceLog.objects.filter(
            activity=activity,
            user=request.user,
            date=occ_date
        ).delete()
        return Response({'status': 'pending', 'date': occ_date.strftime('%Y-%m-%d')})

    @action(detail=True, methods=['post'], url_path='skip')
    def mark_skip(self, request, pk=None):
        activity = self.get_object()
        occ_date_str = request.data.get('date', date.today().strftime('%Y-%m-%d'))
        notes = request.data.get('notes', '')

        try:
            occ_date = datetime.strptime(occ_date_str, '%Y-%m-%d').date()
        except ValueError:
            occ_date = date.today()

        log, _ = ActivityInstanceLog.objects.update_or_create(
            activity=activity,
            user=request.user,
            date=occ_date,
            defaults={'status': 'skipped', 'notes': notes}
        )
        return Response({'status': 'skipped', 'date': occ_date.strftime('%Y-%m-%d')})

    @action(detail=True, methods=['post'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        activity = self.get_object()
        occ_date_str = request.data.get('date')
        new_date_str = request.data.get('new_date')
        new_start_time = request.data.get('new_start_time')
        new_end_time = request.data.get('new_end_time')

        if not occ_date_str:
            return Response({"error": "date is required"}, status=status.HTTP_400_BAD_REQUEST)

        occ_date = datetime.strptime(occ_date_str, '%Y-%m-%d').date()

        defaults = {'status': 'rescheduled'}
        if new_date_str:
            defaults['rescheduled_date'] = datetime.strptime(new_date_str, '%Y-%m-%d').date()
        if new_start_time:
            defaults['rescheduled_start_time'] = datetime.strptime(new_start_time, '%H:%M').time()
        if new_end_time:
            defaults['rescheduled_end_time'] = datetime.strptime(new_end_time, '%H:%M').time()

        log, _ = ActivityInstanceLog.objects.update_or_create(
            activity=activity,
            user=request.user,
            date=occ_date,
            defaults=defaults
        )
        return Response({'status': 'rescheduled', 'log': ActivityInstanceLogSerializer(log).data})

    @action(detail=True, methods=['post'], url_path='duplicate')
    def duplicate(self, request, pk=None):
        activity = self.get_object()
        new_activity = Activity.objects.create(
            user=request.user,
            title=f"{activity.title} (Copy)",
            description=activity.description,
            category=activity.category,
            date=activity.date,
            start_time=activity.start_time,
            end_time=activity.end_time,
            priority=activity.priority,
            reminder_minutes=activity.reminder_minutes,
            recurrence=activity.recurrence,
            selected_weekdays=activity.selected_weekdays,
            end_date=activity.end_date,
            color=activity.color,
            is_active=True,
            is_completed=False,
        )
        return Response(ActivitySerializer(new_activity).data, status=status.HTTP_201_CREATED)
