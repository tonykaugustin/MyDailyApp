from rest_framework import serializers
from .models import Activity, ActivityCompletion


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
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

        start_date = attrs.get(
            "start_date",
            getattr(self.instance, "start_date", None)
        )
        end_date = attrs.get(
            "end_date",
            getattr(self.instance, "end_date", None)
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot precede start date."}
            )

        return attrs


class ActivityCompletionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityCompletion
        fields = "__all__"
        read_only_fields = ["id", "user"]