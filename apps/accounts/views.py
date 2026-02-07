"""
Views for user accounts.

SECURITY NOTES:
- API keys are stored encrypted in the database using EncryptedCharField
- API keys are NEVER returned in API responses (write_only serializer fields)
- UserProfileSerializer explicitly excludes all API key fields
- APIKeySerializer has write_only=True for all key fields and overrides to_representation()
- Frontend never displays API keys - input is always blank
"""
import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserPreferencesSerializer,
    APIKeySerializer
)
from .models import UserPreferences

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        logger.info(f"[REGISTER] Received registration request")
        logger.debug(f"[REGISTER] Request data: {request.data}")
        logger.debug(f"[REGISTER] Request headers: {dict(request.headers)}")
        
        serializer = self.get_serializer(data=request.data)
        
        try:
            logger.debug(f"[REGISTER] Validating serializer...")
            serializer.is_valid(raise_exception=True)
            logger.info(f"[REGISTER] Validation successful")
        except Exception as e:
            logger.error(f"[REGISTER] Validation failed: {str(e)}")
            logger.error(f"[REGISTER] Serializer errors: {serializer.errors}")
            raise
        
        try:
            logger.debug(f"[REGISTER] Creating user...")
            user = serializer.save()
            logger.info(f"[REGISTER] User created successfully: {user.username}")
        except Exception as e:
            logger.error(f"[REGISTER] User creation failed: {str(e)}")
            raise
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        logger.info(f"[REGISTER] Tokens generated for user: {user.username}")
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    """View and update user profile."""
    
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        return self.request.user


class PreferencesView(generics.RetrieveUpdateAPIView):
    """View and update user preferences."""
    
    serializer_class = UserPreferencesSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences


class APIKeyView(generics.UpdateAPIView):
    """Set or update OpenAI API key."""
    
    serializer_class = APIKeySerializer
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'API key updated successfully',
            'use_own_api_key': instance.use_own_api_key
        })


class LogoutView(APIView):
    """Logout endpoint (blacklist refresh token)."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
