from datetime import date, datetime, timedelta
import calendar
from .models import Activity, ActivityInstanceLog

def get_occurrences_for_range(user, range_start, range_end, category_id=None, priority=None):
    """
    Expands recurring and single activities for a user in [range_start, range_end]
    without duplicating database rows.
    """
    if isinstance(range_start, str):
        range_start = datetime.strptime(range_start, '%Y-%m-%d').date()
    if isinstance(range_end, str):
        range_end = datetime.strptime(range_end, '%Y-%m-%d').date()

    activities = Activity.objects.filter(user=user, is_active=True).select_related('category')
    if category_id:
        activities = activities.filter(category_id=category_id)
    if priority:
        activities = activities.filter(priority=priority)

    # Fetch all logs in or around this range
    logs = ActivityInstanceLog.objects.filter(
        user=user,
        date__range=[range_start - timedelta(days=7), range_end + timedelta(days=7)]
    )
    logs_by_key = {(log.activity_id, log.date): log for log in logs}

    occurrences = []

    for act in activities:
        act_start_date = act.date
        act_end_date = act.end_date

        curr = max(act_start_date, range_start)
        max_end = min(range_end, act_end_date) if act_end_date else range_end

        if act.recurrence == 'none':
            if range_start <= act_start_date <= range_end:
                log = logs_by_key.get((act.id, act_start_date))
                status = log.status if log else ('completed' if act.is_completed else 'pending')
                occurrences.append(_format_occurrence(act, act_start_date, status, log))

        elif act.recurrence == 'daily':
            while curr <= max_end:
                if curr >= act_start_date:
                    log = logs_by_key.get((act.id, curr))
                    status = log.status if log else 'pending'
                    occurrences.append(_format_occurrence(act, curr, status, log))
                curr += timedelta(days=1)

        elif act.recurrence == 'weekly':
            # Same weekday as act.date
            target_weekday = act_start_date.weekday()
            while curr <= max_end:
                if curr.weekday() == target_weekday and curr >= act_start_date:
                    log = logs_by_key.get((act.id, curr))
                    status = log.status if log else 'pending'
                    occurrences.append(_format_occurrence(act, curr, status, log))
                curr += timedelta(days=1)

        elif act.recurrence == 'selected_weekdays':
            weekdays = set(act.selected_weekdays or [])
            while curr <= max_end:
                if curr.weekday() in weekdays and curr >= act_start_date:
                    log = logs_by_key.get((act.id, curr))
                    status = log.status if log else 'pending'
                    occurrences.append(_format_occurrence(act, curr, status, log))
                curr += timedelta(days=1)

        elif act.recurrence == 'monthly':
            target_day = act_start_date.day
            curr_month_date = date(curr.year, curr.month, 1)
            while curr_month_date <= max_end:
                _, days_in_month = calendar.monthrange(curr_month_date.year, curr_month_date.month)
                actual_day = min(target_day, days_in_month)
                occurrence_date = date(curr_month_date.year, curr_month_date.month, actual_day)

                if range_start <= occurrence_date <= max_end and occurrence_date >= act_start_date:
                    log = logs_by_key.get((act.id, occurrence_date))
                    status = log.status if log else 'pending'
                    occurrences.append(_format_occurrence(act, occurrence_date, status, log))

                # Advance month
                if curr_month_date.month == 12:
                    curr_month_date = date(curr_month_date.year + 1, 1, 1)
                else:
                    curr_month_date = date(curr_month_date.year, curr_month_date.month + 1, 1)

        elif act.recurrence == 'custom':
            # Treats custom as weekdays or daily
            weekdays = set(act.selected_weekdays) if act.selected_weekdays else set(range(7))
            while curr <= max_end:
                if curr.weekday() in weekdays and curr >= act_start_date:
                    log = logs_by_key.get((act.id, curr))
                    status = log.status if log else 'pending'
                    occurrences.append(_format_occurrence(act, curr, status, log))
                curr += timedelta(days=1)

    # Sort occurrences by occurrence date and start_time
    occurrences.sort(key=lambda x: (x['occurrence_date'], x['start_time']))
    return occurrences

def _format_occurrence(activity, occ_date, status, log=None):
    category_data = None
    if activity.category:
        category_data = {
            'id': activity.category.id,
            'name': activity.category.name,
            'color': activity.category.color,
            'icon': activity.category.icon,
        }

    start_time = activity.start_time
    end_time = activity.end_time

    if log and log.status == 'rescheduled':
        if log.rescheduled_start_time:
            start_time = log.rescheduled_start_time
        if log.rescheduled_end_time:
            end_time = log.rescheduled_end_time

    return {
        'instance_id': f"{activity.id}_{occ_date.strftime('%Y%m%d')}",
        'activity_id': activity.id,
        'title': activity.title,
        'description': activity.description,
        'category': category_data,
        'category_id': activity.category_id,
        'occurrence_date': occ_date.strftime('%Y-%m-%d'),
        'original_date': activity.date.strftime('%Y-%m-%d'),
        'start_time': start_time.strftime('%H:%M'),
        'end_time': end_time.strftime('%H:%M'),
        'priority': activity.priority,
        'reminder_minutes': activity.reminder_minutes,
        'recurrence': activity.recurrence,
        'selected_weekdays': activity.selected_weekdays,
        'color': activity.color,
        'status': status,
        'notes': log.notes if log else '',
        'rescheduled_date': log.rescheduled_date.strftime('%Y-%m-%d') if (log and log.rescheduled_date) else None,
        'is_recurring': activity.recurrence != 'none',
    }

def detect_conflicts(user, check_date, start_time, end_time, exclude_activity_id=None):
    """
    Checks if any activity occurs on check_date that overlaps with start_time and end_time.
    """
    if isinstance(check_date, str):
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%H:%M').time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%H:%M').time()

    occurrences = get_occurrences_for_range(user, check_date, check_date)
    conflicts = []

    for occ in occurrences:
        if exclude_activity_id and occ['activity_id'] == int(exclude_activity_id):
            continue
        if occ['status'] == 'skipped':
            continue

        occ_start = datetime.strptime(occ['start_time'], '%H:%M').time()
        occ_end = datetime.strptime(occ['end_time'], '%H:%M').time()

        # Overlap condition: start_time < occ_end and end_time > occ_start
        if start_time < occ_end and end_time > occ_start:
            conflicts.append(occ)

    return conflicts

