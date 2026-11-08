from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, datetime, timedelta
from django.db.models import Sum
from .models import LearningTopic, LearningResource, LearningMilestone, StudySession
from .serializers import (
    LearningTopicSerializer, LearningResourceSerializer,
    LearningMilestoneSerializer, StudySessionSerializer
)

class LearningTopicViewSet(viewsets.ModelViewSet):
    serializer_class = LearningTopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = LearningTopic.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        topic_status = self.request.query_params.get('status')
        if category:
            qs = qs.filter(category_id=category)
        if topic_status:
            qs = qs.filter(status=topic_status)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='resources')
    def add_resource(self, request, pk=None):
        topic = self.get_object()
        serializer = LearningResourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(topic=topic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='milestones')
    def add_milestone(self, request, pk=None):
        topic = self.get_object()
        serializer = LearningMilestoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(topic=topic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LearningResourceViewSet(viewsets.ModelViewSet):
    serializer_class = LearningResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningResource.objects.filter(topic__user=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle')
    def toggle(self, request, pk=None):
        resource = self.get_object()
        resource.is_completed = not resource.is_completed
        resource.save()
        return Response(LearningResourceSerializer(resource).data)

class LearningMilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = LearningMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningMilestone.objects.filter(topic__user=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle')
    def toggle(self, request, pk=None):
        milestone = self.get_object()
        milestone.is_completed = not milestone.is_completed
        milestone.save()
        return Response(LearningMilestoneSerializer(milestone).data)

class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = StudySession.objects.filter(user=self.request.user)
        topic = self.request.query_params.get('topic')
        category = self.request.query_params.get('category')
        if topic:
            qs = qs.filter(topic_id=topic)
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='today')
    def today_study(self, request):
        today = date.today()
        sessions = StudySession.objects.filter(user=request.user, created_at__date=today)
        total_minutes = sessions.aggregate(total=Sum('duration_minutes'))['total'] or 0
        return Response({
            'total_minutes': total_minutes,
            'total_hours': round(total_minutes / 60.0, 1),
            'sessions_count': sessions.count(),
            'sessions': StudySessionSerializer(sessions, many=True).data
        })
