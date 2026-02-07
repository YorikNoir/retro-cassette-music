"""
Serializers for songs.
"""
from rest_framework import serializers
from .models import Song, Vote, Playlist
from apps.accounts.serializers import UserProfileSerializer


class SongSerializer(serializers.ModelSerializer):
    """Serializer for Song model."""
    
    user = UserProfileSerializer(read_only=True)
    score = serializers.IntegerField(read_only=True)
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Song
        fields = [
            'id', 'user', 'title', 'lyrics', 'description',
            'genre', 'mood', 'duration', 'temperature',
            'audio_file', 'cover_image', 'status', 'error_message',
            'is_public', 'published_at', 'play_count',
            'upvotes', 'downvotes', 'score', 'user_vote',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'audio_file', 'status', 'error_message',
            'play_count', 'upvotes', 'downvotes', 'published_at',
            'created_at', 'updated_at'
        ]
    
    def get_user_vote(self, obj):
        """Get current user's vote on this song."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = Vote.objects.filter(user=request.user, song=obj).first()
            return vote.vote_type if vote else None
        return None


class SongCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating songs."""
    
    lyrics = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    mood = serializers.CharField(required=False, allow_blank=True)
    duration = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Song
        fields = [
            'title', 'lyrics', 'description',
            'genre', 'mood', 'duration', 'temperature'
        ]
    
    def create(self, validated_data):
        user = self.context['request'].user
        # Set empty lyrics to empty string if not provided
        if 'lyrics' not in validated_data:
            validated_data['lyrics'] = ''
        song = Song.objects.create(user=user, **validated_data)
        user.increment_song_count()
        return song


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for Votes."""
    
    class Meta:
        model = Vote
        fields = ['id', 'song', 'vote_type', 'created_at']
        read_only_fields = ['created_at']
    
    def create(self, validated_data):
        user = self.context['request'].user
        song = validated_data['song']
        vote_type = validated_data['vote_type']
        
        # Update or create vote
        vote, created = Vote.objects.update_or_create(
            user=user,
            song=song,
            defaults={'vote_type': vote_type}
        )
        
        return vote


class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for Playlists."""
    
    user = UserProfileSerializer(read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    song_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Song.objects.all(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Playlist
        fields = [
            'id', 'user', 'name', 'description', 'songs', 'song_ids',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        song_ids = validated_data.pop('song_ids', [])
        user = self.context['request'].user
        playlist = Playlist.objects.create(user=user, **validated_data)
        if song_ids:
            playlist.songs.set(song_ids)
        return playlist
    
    def update(self, instance, validated_data):
        song_ids = validated_data.pop('song_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if song_ids is not None:
            instance.songs.set(song_ids)
        
        return instance
