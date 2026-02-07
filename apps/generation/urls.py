"""
URL patterns for generation app.
"""
from django.urls import path

from .views import GenerateLyricsView, TaskStatusView

app_name = 'generation'

urlpatterns = [
    path('lyrics/', GenerateLyricsView.as_view(), name='generate_lyrics'),
    path('task/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
]
