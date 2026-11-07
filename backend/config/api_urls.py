from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from schedules.views import ActivityViewSet
from tasks.views import TaskViewSet
from learning.views import (
    LearningProgressViewSet,
    StudySessionViewSet,
)
from notifications.views import NotificationPreferenceView
from .dashboard import dashboard


router = DefaultRouter()

router.register(
    "activities",
    ActivityViewSet,
    basename="activities"
)

router.register(
    "tasks",
    TaskViewSet,
    basename="tasks"
)

router.register(
    "learning",
    LearningProgressViewSet,
    basename="learning"
)

router.register(
    "study-sessions",
    StudySessionViewSet,
    basename="study-sessions"
)


urlpatterns = [
    path("", include(router.urls)),

    path("dashboard/", dashboard),

    path(
        "auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    path(
        "notification-preferences/",
        NotificationPreferenceView.as_view(),
    ),
]