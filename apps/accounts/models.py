"""
User account models.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField


class User(AbstractUser):
    """Custom user model with additional fields."""
    
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # API Key for OpenAI (encrypted)
    openai_api_key = EncryptedCharField(max_length=255, blank=True, null=True)
    use_own_api_key = models.BooleanField(default=False)
    
    # Stats
    total_songs_created = models.IntegerField(default=0)
    total_songs_published = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def increment_song_count(self):
        """Increment total songs created."""
        self.total_songs_created += 1
        self.save(update_fields=['total_songs_created'])
    
    def increment_published_count(self):
        """Increment total published songs."""
        self.total_songs_published += 1
        self.save(update_fields=['total_songs_published'])


class UserPreferences(models.Model):
    """User preferences for generation defaults."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Default generation settings
    default_genre = models.CharField(max_length=50, blank=True)
    default_duration = models.IntegerField(default=30)  # seconds
    default_temperature = models.FloatField(default=1.0)
    
    # UI preferences
    theme_variant = models.CharField(max_length=20, default='classic')  # classic, neon, vintage
    auto_play = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s preferences"
