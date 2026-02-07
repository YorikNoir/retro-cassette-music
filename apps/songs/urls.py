"""
URL patterns for songs app.
"""
from django.urls import path

from .views import (
    SongListView,
    SongDetailView,
    SongCreateView,
    SongPublishView,
    SongPlayView,
    VoteView,
    PlaylistListCreateView,
    PlaylistDetailView,
)

app_name = 'songs'

urlpatterns = [
    # Songs
    path('', SongListView.as_view(), name='song_list'),
    path('create/', SongCreateView.as_view(), name='song_create'),
    path('<int:pk>/', SongDetailView.as_view(), name='song_detail'),
    path('<int:pk>/publish/', SongPublishView.as_view(), name='song_publish'),
    path('<int:pk>/play/', SongPlayView.as_view(), name='song_play'),
    path('<int:pk>/vote/', VoteView.as_view(), name='song_vote'),
    
    # Playlists
    path('playlists/', PlaylistListCreateView.as_view(), name='playlist_list'),
    path('playlists/<int:pk>/', PlaylistDetailView.as_view(), name='playlist_detail'),
]
