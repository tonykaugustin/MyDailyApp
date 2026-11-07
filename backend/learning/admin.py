from django.contrib import admin
from .models import LearningProgress, StudySession

admin.site.register(LearningProgress)
admin.site.register(StudySession)