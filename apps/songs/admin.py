from django.contrib import admin
from .models import Song, Vote, Playlist


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'genre', 'status', 'is_public', 'score', 'play_count', 'created_at']
    list_filter = ['status', 'is_public', 'genre', 'mood', 'created_at']
    search_fields = ['title', 'user__username', 'lyrics']
    readonly_fields = ['created_at', 'updated_at', 'play_count', 'upvotes', 'downvotes']
    
    def score(self, obj):
        return obj.score
    score.short_description = 'Score'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'song', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['user__username', 'song__title']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'user__username']
