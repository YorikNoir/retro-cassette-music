"""
Serializers for user accounts.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserPreferences

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Create default preferences
        UserPreferences.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'avatar',
            'total_songs_created', 'total_songs_published',
            'created_at'
        ]
        read_only_fields = ['total_songs_created', 'total_songs_published', 'created_at']


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""
    
    class Meta:
        model = UserPreferences
        fields = [
            'default_genre', 'default_duration', 'default_temperature',
            'theme_variant', 'auto_play'
        ]


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for setting OpenAI API key."""
    
    openai_api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['openai_api_key', 'use_own_api_key']
    
    def update(self, instance, validated_data):
        if 'openai_api_key' in validated_data:
            api_key = validated_data['openai_api_key']
            if api_key:
                instance.openai_api_key = api_key
                instance.use_own_api_key = True
            else:
                instance.openai_api_key = None
                instance.use_own_api_key = False
        
        instance.save()
        return instance
