"""
Serializers for user accounts.
"""
import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import UserPreferences

logger = logging.getLogger(__name__)
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        logger.debug(f"[REGISTER SERIALIZER] Validating data: {list(data.keys())}")
        
        if 'password' not in data:
            logger.error(f"[REGISTER SERIALIZER] Missing password field")
            raise serializers.ValidationError({"password": "This field is required."})
        
        if 'password_confirm' not in data:
            logger.error(f"[REGISTER SERIALIZER] Missing password_confirm field")
            raise serializers.ValidationError({"password_confirm": "This field is required."})
        
        if data['password'] != data['password_confirm']:
            logger.error(f"[REGISTER SERIALIZER] Passwords do not match")
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        
        logger.debug(f"[REGISTER SERIALIZER] Validation successful")
        return data
    
    def create(self, validated_data):
        logger.debug(f"[REGISTER SERIALIZER] Creating user with username: {validated_data.get('username')}")
        validated_data.pop('password_confirm')
        
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
            logger.info(f"[REGISTER SERIALIZER] User created: {user.username}")
        except IntegrityError as e:
            logger.error(f"[REGISTER SERIALIZER] IntegrityError: {str(e)}")
            error_msg = str(e).lower()
            if 'username' in error_msg:
                raise serializers.ValidationError({"username": "This username is already taken."})
            elif 'email' in error_msg:
                raise serializers.ValidationError({"email": "This email is already registered."})
            else:
                raise serializers.ValidationError({"non_field_errors": "A user with these details already exists."})
        except Exception as e:
            logger.error(f"[REGISTER SERIALIZER] Failed to create user: {str(e)}")
            logger.exception(e)
            raise serializers.ValidationError({"non_field_errors": f"Failed to create user: {str(e)}"})
        
        # Create default preferences
        try:
            UserPreferences.objects.create(user=user)
            logger.debug(f"[REGISTER SERIALIZER] User preferences created for: {user.username}")
        except Exception as e:
            logger.error(f"[REGISTER SERIALIZER] Failed to create preferences: {str(e)}")
            logger.exception(e)
            # Don't fail registration if preferences fail - user can set them later
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile.
    
    SECURITY: API keys (llm_api_key, openai_api_key) are NEVER included 
    in this serializer to prevent exposure to clients.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'avatar',
            'total_songs_created', 'total_songs_published',
            'created_at',
            'llm_provider', 'llm_model', 'custom_api_base_url', 'custom_provider_name', 'use_own_api_key'
        ]
        read_only_fields = ['total_songs_created', 'total_songs_published', 'created_at']
    
    def to_representation(self, instance):
        """Ensure API keys are NEVER exposed in any response."""
        data = super().to_representation(instance)
        # Explicitly remove any API key fields if they somehow got included
        data.pop('llm_api_key', None)
        data.pop('openai_api_key', None)
        return data


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""
    
    class Meta:
        model = UserPreferences
        fields = [
            'default_genre', 'default_duration', 'default_temperature',
            'theme_variant', 'auto_play'
        ]


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for setting LLM provider configuration.
    
    SECURITY:
    - API keys are write-only and encrypted in database using EncryptedCharField
    - API keys are NEVER returned in responses (write_only=True)
    - Empty string API keys are converted to None
    - to_representation() explicitly removes any API key fields from responses
    """
    
    llm_api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)
    openai_api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)  # Legacy support
    
    class Meta:
        model = User
        fields = [
            'llm_provider',
            'llm_api_key',
            'llm_model',
            'custom_api_base_url',
            'custom_provider_name',
            'use_own_api_key',
            'openai_api_key'  # Legacy
        ]
    
    def to_representation(self, instance):
        """Override to ensure API keys are NEVER exposed in responses."""
        data = super().to_representation(instance)
        # Explicitly remove API key fields (they should already be excluded via write_only)
        data.pop('llm_api_key', None)
        data.pop('openai_api_key', None)
        return data
    
    def validate_llm_api_key(self, value):
        """Convert empty strings to None."""
        return value.strip() if value and value.strip() else None
    
    def validate_openai_api_key(self, value):
        """Convert empty strings to None."""
        return value.strip() if value and value.strip() else None
    
    def update(self, instance, validated_data):
        # Handle legacy openai_api_key field
        if 'openai_api_key' in validated_data:
            api_key = validated_data.pop('openai_api_key')
            if api_key:
                validated_data['llm_api_key'] = api_key
                validated_data['llm_provider'] = 'openai'
                validated_data['use_own_api_key'] = True
        
        # Update provider and key
        if 'llm_api_key' in validated_data:
            api_key = validated_data['llm_api_key']
            if api_key:
                instance.llm_api_key = api_key
                instance.use_own_api_key = True
            else:
                instance.llm_api_key = None
                instance.use_own_api_key = False
        
        # Update provider
        if 'llm_provider' in validated_data:
            instance.llm_provider = validated_data['llm_provider']
        
        # Update model
        if 'llm_model' in validated_data:
            instance.llm_model = validated_data['llm_model']
        
        # Update custom provider details
        if 'custom_api_base_url' in validated_data:
            instance.custom_api_base_url = validated_data['custom_api_base_url']
        
        if 'custom_provider_name' in validated_data:
            instance.custom_provider_name = validated_data['custom_provider_name']
        
        instance.save()
        return instance
