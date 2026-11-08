from rest_framework import serializers
from .models import Task, SubTask
from categories.serializers import CategorySerializer
from categories.models import Category

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'task', 'title', 'is_completed', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    subtasks_count = serializers.IntegerField(source='subtasks.count', read_only=True)
    completed_subtasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'category', 'category_details',
            'priority', 'status', 'due_date', 'due_time', 'estimated_minutes',
            'actual_minutes', 'tags', 'is_archived', 'subtasks', 'subtasks_count',
            'completed_subtasks_count', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']

    def get_completed_subtasks_count(self, obj):
        return obj.subtasks.filter(is_completed=True).count()

