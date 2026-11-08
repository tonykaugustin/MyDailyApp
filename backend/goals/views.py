from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Goal, GoalMilestone
from .serializers import GoalSerializer, GoalMilestoneSerializer

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Goal.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        timeframe = self.request.query_params.get('timeframe')
        goal_status = self.request.query_params.get('status')

        if category:
            qs = qs.filter(category_id=category)
        if timeframe:
            qs = qs.filter(timeframe=timeframe)
        if goal_status:
            qs = qs.filter(status=goal_status)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='progress')
    def update_progress(self, request, pk=None):
        goal = self.get_object()
        new_val = request.data.get('current_value')
        if new_val is None:
            return Response({"error": "current_value is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            goal.current_value = float(new_val)
            if goal.current_value >= goal.target_value and goal.status == 'in_progress':
                goal.status = 'achieved'
            goal.save()
            return Response(GoalSerializer(goal).data)
        except ValueError:
            return Response({"error": "Invalid value for current_value"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='milestones')
    def add_milestone(self, request, pk=None):
        goal = self.get_object()
        serializer = GoalMilestoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(goal=goal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoalMilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = GoalMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalMilestone.objects.filter(goal__user=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle')
    def toggle(self, request, pk=None):
        milestone = self.get_object()
        milestone.is_completed = not milestone.is_completed
        milestone.save()
        return Response(GoalMilestoneSerializer(milestone).data)
