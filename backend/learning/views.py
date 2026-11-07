from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import LearningProgress, StudySession
from .serializers import (
    LearningProgressSerializer,
    StudySessionSerializer,
)


class LearningProgressViewSet(viewsets.ModelViewSet):

    serializer_class = LearningProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LearningProgress.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudySessionViewSet(viewsets.ModelViewSet):

    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StudySession.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)