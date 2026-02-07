"""
Views for user library.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum

from apps.songs.models import Song


class LibraryStatsView(APIView):
    """Get user library statistics."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get song stats
        songs = Song.objects.filter(user=user)
        
        stats = {
            'total_songs': songs.count(),
            'completed_songs': songs.filter(status='completed').count(),
            'generating_songs': songs.filter(status='generating').count(),
            'failed_songs': songs.filter(status='failed').count(),
            'published_songs': songs.filter(is_public=True).count(),
            'total_plays': songs.aggregate(Sum('play_count'))['play_count__sum'] or 0,
            'total_upvotes': songs.aggregate(Sum('upvotes'))['upvotes__sum'] or 0,
            'genres': songs.values('genre').annotate(count=Count('genre')),
        }
        
        return Response(stats)
