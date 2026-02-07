"""
Views for songs.
"""
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Song, Vote, Playlist
from .serializers import (
    SongSerializer,
    SongCreateSerializer,
    VoteSerializer,
    PlaylistSerializer
)
from .filters import SongFilter


class SongListView(generics.ListAPIView):
    """List all public songs or user's songs."""
    
    serializer_class = SongSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SongFilter
    search_fields = ['title', 'description', 'lyrics']
    ordering_fields = ['created_at', 'upvotes', 'play_count', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if self.request.query_params.get('my_songs'):
            # User's own songs
            return Song.objects.filter(user=self.request.user)
        else:
            # Public songs
            return Song.objects.filter(is_public=True, status='completed')
    
    def get_permissions(self):
        if self.request.query_params.get('my_songs'):
            return [IsAuthenticated()]
        return [AllowAny()]


class SongDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a song."""
    
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only access their own songs or public songs
        return Song.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )
    
    def perform_destroy(self, instance):
        # Only owner can delete
        if instance.user != self.request.user:
            raise PermissionError("You can only delete your own songs.")
        instance.delete()


class SongCreateView(generics.CreateAPIView):
    """Create a new song."""
    
    serializer_class = SongCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        song = serializer.save()
        
        # Trigger async generation task
        from apps.generation.tasks import generate_song_task
        generate_song_task.delay(song.id)
        
        return Response(
            SongSerializer(song).data,
            status=status.HTTP_201_CREATED
        )


class SongPublishView(APIView):
    """Publish or unpublish a song."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            song = Song.objects.get(pk=pk, user=request.user)
        except Song.DoesNotExist:
            return Response(
                {'error': 'Song not found or you do not have permission.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        action = request.data.get('action', 'publish')
        
        if action == 'publish':
            if song.status != 'completed':
                return Response(
                    {'error': 'Only completed songs can be published.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            song.publish()
            message = 'Song published successfully.'
        elif action == 'unpublish':
            song.unpublish()
            message = 'Song unpublished successfully.'
        else:
            return Response(
                {'error': 'Invalid action. Use "publish" or "unpublish".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'message': message,
            'song': SongSerializer(song).data
        })


class SongPlayView(APIView):
    """Increment play count."""
    
    def post(self, request, pk):
        try:
            song = Song.objects.get(pk=pk, is_public=True)
        except Song.DoesNotExist:
            # Also allow owner to play their own unpublished songs
            if request.user.is_authenticated:
                try:
                    song = Song.objects.get(pk=pk, user=request.user)
                except Song.DoesNotExist:
                    return Response(
                        {'error': 'Song not found.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {'error': 'Song not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        song.increment_play_count()
        return Response({'play_count': song.play_count})


class VoteView(APIView):
    """Vote on a song."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            song = Song.objects.get(pk=pk, is_public=True)
        except Song.DoesNotExist:
            return Response(
                {'error': 'Song not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        vote_type = request.data.get('vote_type')
        if vote_type not in ['up', 'down']:
            return Response(
                {'error': 'Invalid vote type. Use "up" or "down".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = VoteSerializer(
            data={'song': pk, 'vote_type': vote_type},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Refresh song data
        song.refresh_from_db()
        
        return Response({
            'message': 'Vote recorded.',
            'upvotes': song.upvotes,
            'downvotes': song.downvotes,
            'score': song.score
        })
    
    def delete(self, request, pk):
        """Remove vote."""
        try:
            vote = Vote.objects.get(user=request.user, song_id=pk)
            vote.delete()
            
            song = Song.objects.get(pk=pk)
            return Response({
                'message': 'Vote removed.',
                'upvotes': song.upvotes,
                'downvotes': song.downvotes,
                'score': song.score
            })
        except Vote.DoesNotExist:
            return Response(
                {'error': 'Vote not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class PlaylistListCreateView(generics.ListCreateAPIView):
    """List and create playlists."""
    
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)


class PlaylistDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a playlist."""
    
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)
