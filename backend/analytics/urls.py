from django.urls import path
from .views import DashboardSummaryView, AnalyticsOverviewView

urlpatterns = [
    path('dashboard/', DashboardSummaryView.as_view(), name='dashboard_summary'),
    path('overview/', AnalyticsOverviewView.as_view(), name='analytics_overview'),
]

