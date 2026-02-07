"""
URL patterns for library app.
"""
from django.urls import path

from .views import LibraryStatsView

app_name = 'library'

urlpatterns = [
    path('stats/', LibraryStatsView.as_view(), name='stats'),
]
