from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LearningTopicViewSet, LearningResourceViewSet,
    LearningMilestoneViewSet, StudySessionViewSet
)

router = DefaultRouter()
router.register(r'topics', LearningTopicViewSet, basename='learning_topic')
router.register(r'resources', LearningResourceViewSet, basename='learning_resource')
router.register(r'milestones', LearningMilestoneViewSet, basename='learning_milestone')
router.register(r'sessions', StudySessionViewSet, basename='study_session')

urlpatterns = [
    path('', include(router.urls)),
]

