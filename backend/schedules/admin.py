from django.contrib import admin
from .models import Activity, ActivityCompletion


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "category",
        "start_time",
        "end_time",
        "recurrence",
        "is_active",
    )

    list_filter = ("category", "recurrence", "is_active")
    search_fields = ("title", "user__username")


@admin.register(ActivityCompletion)
class ActivityCompletionAdmin(admin.ModelAdmin):
    list_display = (
        "activity",
        "user",
        "date",
        "status",
    )

    list_filter = ("status", "date")