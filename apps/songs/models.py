"""
Song models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Song(models.Model):
    """Model for generated songs."""
    
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    GENRE_CHOICES = [
        ('pop', 'Pop'),
        ('rock', 'Rock'),
        ('jazz', 'Jazz'),
        ('classical', 'Classical'),
        ('electronic', 'Electronic'),
        ('hiphop', 'Hip Hop'),
        ('country', 'Country'),
        ('rnb', 'R&B'),
        ('blues', 'Blues'),
        ('metal', 'Metal'),
        ('folk', 'Folk'),
        ('ambient', 'Ambient'),
        ('other', 'Other'),
    ]
    
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('energetic', 'Energetic'),
        ('calm', 'Calm'),
        ('romantic', 'Romantic'),
        ('melancholic', 'Melancholic'),
        ('aggressive', 'Aggressive'),
        ('mysterious', 'Mysterious'),
        ('uplifting', 'Uplifting'),
        ('dark', 'Dark'),
    ]
    
    # Owner
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='songs')
    
    # Song metadata
    title = models.CharField(max_length=200)
    lyrics = models.TextField()
    description = models.TextField(blank=True)
    
    # Generation parameters
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='pop')
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES, blank=True)
    duration = models.IntegerField(default=30, validators=[MinValueValidator(10), MaxValueValidator(180)])
    temperature = models.FloatField(default=1.0, validators=[MinValueValidator(0.1), MaxValueValidator(2.0)])
    
    # Files
    audio_file = models.FileField(upload_to='songs/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    error_message = models.TextField(blank=True)
    
    # Publishing
    is_public = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    play_count = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_public', '-upvotes']),
            models.Index(fields=['genre']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
    @property
    def score(self):
        """Calculate song score (upvotes - downvotes)."""
        return self.upvotes - self.downvotes
    
    def increment_play_count(self):
        """Increment play count."""
        self.play_count += 1
        self.save(update_fields=['play_count'])
    
    def publish(self):
        """Publish the song."""
        from django.utils import timezone
        self.is_public = True
        self.published_at = timezone.now()
        self.save(update_fields=['is_public', 'published_at'])
        self.user.increment_published_count()
    
    def unpublish(self):
        """Unpublish the song."""
        self.is_public = False
        self.published_at = None
        self.save(update_fields=['is_public', 'published_at'])


class Vote(models.Model):
    """Model for song votes."""
    
    VOTE_TYPES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'song']
        indexes = [
            models.Index(fields=['song', 'vote_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.vote_type}voted {self.song.title}"
    
    def save(self, *args, **kwargs):
        """Update song vote counts when saving."""
        # Check if this is an update or new vote
        if self.pk:
            old_vote = Vote.objects.get(pk=self.pk)
            # Remove old vote count
            if old_vote.vote_type == 'up':
                self.song.upvotes -= 1
            else:
                self.song.downvotes -= 1
        
        # Add new vote count
        if self.vote_type == 'up':
            self.song.upvotes += 1
        else:
            self.song.downvotes += 1
        
        self.song.save(update_fields=['upvotes', 'downvotes'])
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Update song vote counts when deleting."""
        if self.vote_type == 'up':
            self.song.upvotes -= 1
        else:
            self.song.downvotes -= 1
        self.song.save(update_fields=['upvotes', 'downvotes'])
        super().delete(*args, **kwargs)


class Playlist(models.Model):
    """User playlists."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"
