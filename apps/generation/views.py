"""
Views for generation endpoints.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .tasks import generate_lyrics_only_task
from celery.result import AsyncResult


class GenerateLyricsView(APIView):
    """Generate lyrics preview without creating a song."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response(
                {'error': 'Prompt is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get API key if user wants to use their own
        api_key = None
        if request.user.use_own_api_key and request.user.openai_api_key:
            api_key = request.user.openai_api_key
        
        temperature = request.data.get('temperature', 0.8)
        
        # Run synchronously for immediate response
        # In production, you might want to make this async too
        try:
            from .generator import get_lyrics_generator
            lyrics_gen = get_lyrics_generator(api_key=api_key)
            lyrics = lyrics_gen.generate(prompt, temperature=temperature)
            
            return Response({
                'status': 'success',
                'lyrics': lyrics
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskStatusView(APIView):
    """Check status of a Celery task."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        task = AsyncResult(task_id)
        
        response_data = {
            'task_id': task_id,
            'status': task.state,
        }
        
        if task.state == 'PENDING':
            response_data['message'] = 'Task is waiting to be processed'
        elif task.state == 'STARTED':
            response_data['message'] = 'Task is currently running'
        elif task.state == 'SUCCESS':
            response_data['result'] = task.result
        elif task.state == 'FAILURE':
            response_data['error'] = str(task.info)
        
        return Response(response_data)
