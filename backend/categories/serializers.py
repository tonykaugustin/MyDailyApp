from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    activities_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'icon', 'type', 'is_active', 'activities_count', 'tasks_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_activities_count(self, obj):
        return getattr(obj, 'activities', None).count() if hasattr(obj, 'activities') else 0

    def get_tasks_count(self, obj):
        return getattr(obj, 'tasks', None).count() if hasattr(obj, 'tasks') else 0

