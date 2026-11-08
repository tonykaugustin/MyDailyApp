from rest_framework import serializers
from datetime import date
from .models import Habit, HabitLog
from categories.serializers import CategorySerializer
from categories.models import Category

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'date', 'completed', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class HabitSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    is_completed_today = serializers.SerializerMethodField()
    weekly_history = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            'id', 'title', 'description', 'category', 'category_details',
            'frequency', 'target_days_per_week', 'time_of_day', 'color', 'icon',
            'current_streak', 'best_streak', 'is_active', 'is_completed_today',
            'weekly_history', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_streak', 'best_streak', 'created_at', 'updated_at']

    def get_is_completed_today(self, obj):
        today = date.today()
        return obj.logs.filter(date=today, completed=True).exists()

    def get_weekly_history(self, obj):
        from datetime import timedelta
        today = date.today()
        # Last 7 days
        days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        completed_dates = set(
            obj.logs.filter(date__in=days, completed=True).values_list('date', flat=True)
        )
        return [
            {
                'date': d.strftime('%Y-%m-%d'),
                'day_name': d.strftime('%a'),
                'completed': d in completed_dates
            }
            for d in days
        ]

