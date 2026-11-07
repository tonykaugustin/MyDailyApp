from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Activity, ActivityCompletion
from .serializers import (
    ActivitySerializer,
    ActivityCompletionSerializer,
)


class ActivityViewSet(viewsets.ModelViewSet):

    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Activity.objects.filter(
            user=self.request.user
        )

        date = self.request.query_params.get("date")
        category = self.request.query_params.get("category")

        if date:
            queryset = queryset.filter(start_date__lte=date).filter(
                models_q_end_date(date)
            )

        if category:
            queryset = queryset.filter(category=category)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        activity = self.get_object()
        today = timezone.localdate()

        completion, created = ActivityCompletion.objects.get_or_create(
            activity=activity,
            date=today,
            defaults={
                "user": request.user,
                "status": ActivityCompletion.Status.COMPLETED,
                "completed_at": timezone.now(),
            },
        )

        if not created:
            completion.status = ActivityCompletion.Status.COMPLETED
            completion.completed_at = timezone.now()
            completion.save()

        return Response(
            ActivityCompletionSerializer(completion).data,
            status=status.HTTP_200_OK,
        )


def models_q_end_date(date):
    from django.db.models import Q

    return Q(end_date__isnull=True) | Q(end_date__gte=date)