from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/timetable/', include('timetable.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/learning/', include('learning.urls')),
    path('api/habits/', include('habits.urls')),
    path('api/goals/', include('goals.urls')),
    path('api/notes/', include('notes.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/analytics/', include('analytics.urls')),
]
