from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date
from django.utils import timezone
from .models import Task, SubTask
from .serializers import TaskSerializer, SubTaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Task.objects.filter(user=self.request.user)
        status_param = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        category = self.request.query_params.get('category')
        archived = self.request.query_params.get('archived')
        today_only = self.request.query_params.get('today')

        if status_param:
            qs = qs.filter(status=status_param)
        if priority:
            qs = qs.filter(priority=priority)
        if category:
            qs = qs.filter(category_id=category)
        if archived is not None:
            qs = qs.filter(is_archived=(archived.lower() == 'true'))
        else:
            qs = qs.filter(is_archived=False)

        if today_only:
            today = date.today()
            qs = qs.filter(due_date=today)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle-complete')
    def toggle_complete(self, request, pk=None):
        task = self.get_object()
        if task.status == 'completed':
            task.status = 'todo'
            task.completed_at = None
        else:
            task.status = 'completed'
            task.completed_at = timezone.now()
        task.save()
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=['post'], url_path='subtasks')
    def add_subtask(self, request, pk=None):
        task = self.get_object()
        title = request.data.get('title')
        if not title:
            return Response({"error": "title is required"}, status=status.HTTP_400_BAD_REQUEST)

        order = task.subtasks.count()
        subtask = SubTask.objects.create(task=task, title=title, order=order)
        return Response(SubTaskSerializer(subtask).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='today')
    def today_tasks(self, request):
        today = date.today()
        tasks = Task.objects.filter(user=request.user, due_date=today, is_archived=False)
        return Response(TaskSerializer(tasks, many=True).data)

class SubTaskViewSet(viewsets.ModelViewSet):
    serializer_class = SubTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SubTask.objects.filter(task__user=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle')
    def toggle(self, request, pk=None):
        subtask = self.get_object()
        subtask.is_completed = not subtask.is_completed
        subtask.save()
        return Response(SubTaskSerializer(subtask).data)
