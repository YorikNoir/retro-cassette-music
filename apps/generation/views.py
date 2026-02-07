"""
Views for generation endpoints.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings

from .tasks import generate_lyrics_only_task
from .task_manager import get_task_manager


class GenerateLyricsView(APIView):
    """Generate lyrics preview without creating a song."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        prompt = request.data.get('prompt')
        instructions = request.data.get('instructions', '')
        
        if not prompt:
            return Response(
                {'error': 'Prompt is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Combine prompt with instructions if provided
        full_prompt = prompt
        if instructions:
            full_prompt = f"{prompt}\n\nAdditional instructions: {instructions}"
        
        if settings.DEBUG:
            print(f"[LYRICS] Generating with prompt: {full_prompt[:100]}...")
        
        # Get user's LLM provider configuration
        provider = None
        api_key = None
        base_url = None
        model = None
        
        if request.user.use_own_api_key:
            provider = getattr(request.user, 'llm_provider', 'local')
            api_key = getattr(request.user, 'llm_api_key', None)
            model = getattr(request.user, 'llm_model', None)
            
            # For backwards compatibility with openai_api_key field
            if not api_key:
                api_key = getattr(request.user, 'openai_api_key', None)
                if api_key:
                    provider = 'openai'
            
            # Get custom base URL if provider is custom
            if provider == 'custom':
                base_url = getattr(request.user, 'custom_api_base_url', None)
        
        temperature = request.data.get('temperature', 0.8)
        
        # Run synchronously for immediate response
        try:
            from .generator import get_lyrics_generator
            
            # Create lyrics generator with user's provider configuration
            lyrics_gen = get_lyrics_generator(
                provider=provider,
                api_key=api_key,
                base_url=base_url if provider == 'custom' else None,
                model=model
            )
            
            lyrics = lyrics_gen.generate(full_prompt, temperature=temperature)
            
            # Handle both dict and string responses (backwards compatibility)
            if isinstance(lyrics, dict):
                lyrics_text = lyrics.get('lyrics', '')
                style_text = lyrics.get('style', '')
            else:
                lyrics_text = lyrics
                style_text = ''
            
            if settings.DEBUG:
                print(f"[LYRICS] Generated {len(lyrics_text)} chars lyrics, {len(style_text)} chars style")
                print(f"[LYRICS] Response: status=success, lyrics_len={len(lyrics_text)}, style_len={len(style_text)}")
            
            response_data = {
                'status': 'success',
                'lyrics': lyrics_text,
                'style': style_text
            }
            
            return Response(response_data)
        except Exception as e:
            if settings.DEBUG:
                print(f"[LYRICS] Error: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskStatusView(APIView):
    """Check status of a background task."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        task_manager = get_task_manager()
        is_active = task_manager.is_task_active(task_id)
        
        response_data = {
            'task_id': task_id,
            'status': 'RUNNING' if is_active else 'COMPLETED',
        }
        
        if is_active:
            response_data['message'] = 'Task is currently running'
        else:
            response_data['message'] = 'Task completed or not found'
        
        return Response(response_data)
