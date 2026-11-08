from rest_framework import serializers
from .models import Activity, ActivityInstanceLog
from categories.serializers import CategorySerializer
from categories.models import Category

class ActivitySerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'description', 'category', 'category_details',
            'date', 'start_time', 'end_time', 'priority', 'reminder_minutes',
            'recurrence', 'selected_weekdays', 'end_date', 'color',
            'is_active', 'is_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_time = attrs.get('start_time') or (self.instance.start_time if self.instance else None)
        end_time = attrs.get('end_time') or (self.instance.end_time if self.instance else None)

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})

        return attrs

class ActivityInstanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityInstanceLog
        fields = ['id', 'activity', 'date', 'status', 'rescheduled_date', 'rescheduled_start_time', 'rescheduled_end_time', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

