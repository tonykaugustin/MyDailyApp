from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet, GoalMilestoneViewSet

router = DefaultRouter()
router.register(r'milestones', GoalMilestoneViewSet, basename='goal_milestone')
router.register(r'', GoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
]

