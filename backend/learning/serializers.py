from rest_framework import serializers
from .models import LearningProgress, StudySession


class LearningProgressSerializer(serializers.ModelSerializer):

    class Meta:
        model = LearningProgress
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "progress_percentage",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        total = attrs.get(
            "total_lessons",
            getattr(self.instance, "total_lessons", 0)
        )
        completed = attrs.get(
            "completed_lessons",
            getattr(self.instance, "completed_lessons", 0)
        )

        if completed > total:
            raise serializers.ValidationError(
                {"completed_lessons": "Cannot exceed total lessons."}
            )

        return attrs


class StudySessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudySession
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "duration_minutes",
            "created_at",
        ]

    def validate(self, attrs):
        start = attrs.get(
            "start_time",
            getattr(self.instance, "start_time", None)
        )
        end = attrs.get(
            "end_time",
            getattr(self.instance, "end_time", None)
        )

        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )

        return attrs