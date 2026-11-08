from rest_framework import serializers
from .models import LearningTopic, LearningResource, LearningMilestone, StudySession
from categories.serializers import CategorySerializer
from categories.models import Category

class LearningResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningResource
        fields = ['id', 'topic', 'title', 'type', 'url', 'notes', 'is_completed', 'created_at']
        read_only_fields = ['id', 'created_at']

class LearningMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningMilestone
        fields = ['id', 'topic', 'title', 'target_date', 'is_completed', 'created_at']
        read_only_fields = ['id', 'created_at']

class LearningTopicSerializer(serializers.ModelSerializer):
    resources = LearningResourceSerializer(many=True, read_only=True)
    milestones = LearningMilestoneSerializer(many=True, read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = LearningTopic
        fields = [
            'id', 'title', 'description', 'category', 'category_details',
            'target_hours', 'logged_hours', 'color', 'icon', 'status',
            'progress_percentage', 'resources', 'milestones', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class StudySessionSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = StudySession
        fields = [
            'id', 'topic', 'topic_title', 'category', 'category_name',
            'title', 'session_type', 'duration_minutes', 'notes', 'rating',
            'started_at', 'ended_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

