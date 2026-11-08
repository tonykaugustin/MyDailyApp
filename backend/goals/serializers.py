from rest_framework import serializers
from .models import Goal, GoalMilestone
from categories.serializers import CategorySerializer
from categories.models import Category

class GoalMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalMilestone
        fields = ['id', 'goal', 'title', 'target_date', 'is_completed', 'created_at']
        read_only_fields = ['id', 'created_at']

class GoalSerializer(serializers.ModelSerializer):
    milestones = GoalMilestoneSerializer(many=True, read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'description', 'category', 'category_details',
            'timeframe', 'target_date', 'target_value', 'current_value', 'unit',
            'status', 'progress_percentage', 'milestones', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

