"""
Background tasks for async song generation.
Uses simple threading instead of Celery - no Redis required!
"""
from django.conf import settings
import logging
import os
import uuid

from .task_manager import submit_background_task

logger = logging.getLogger(__name__)


def _generate_song_worker(song_id):
    """
    Worker function to generate music for a song.
    Runs in a background thread.
    
    Args:
        song_id: ID of the Song object
    """
    from apps.songs.models import Song
    from .generator import get_lyrics_generator, get_music_generator
    
    try:
        song = Song.objects.get(id=song_id)
        logger.info(f"[TASK] Starting generation for song {song_id}: {song.title}")
        
        # Update status
        song.status = 'generating'
        song.save(update_fields=['status'])
        
        # Get API key if user has their own
        api_key = None
        if song.user.use_own_api_key and song.user.openai_api_key:
            api_key = song.user.openai_api_key
        
        # Generate lyrics if needed (user might have provided their own)
        if not song.lyrics or song.lyrics.strip() == "":
            logger.info(f"[TASK] Generating lyrics for song {song_id}...")
            lyrics_gen = get_lyrics_generator(api_key=api_key)
            mood_part = f" with a {song.mood} mood" if song.mood else ""
            prompt = f"Write song lyrics for a {song.genre} song{mood_part}. Title: {song.title}"
            if song.description:
                prompt += f"\n\nStyle: {song.description}"
            song.lyrics = lyrics_gen.generate(prompt, temperature=song.temperature)
            song.save(update_fields=['lyrics'])
        
        # Generate music
        logger.info(f"[TASK] Generating music for song {song_id}...")
        music_gen = get_music_generator()
        audio_data = music_gen.generate(
            lyrics=song.lyrics,
            genre=song.genre,
            mood=song.mood or '',
            duration=song.duration,
            temperature=song.temperature,
            description=song.description or ''
        )
        
        # Save audio file
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(settings.MEDIA_ROOT, 'songs', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write audio
        import soundfile as sf
        import numpy as np
        if isinstance(audio_data, np.ndarray):
            sf.write(filepath, audio_data, samplerate=44100)
        else:
            # If audio_data is already a path
            import shutil
            shutil.move(audio_data, filepath)
        
        # Update song
        song.audio_file = f'songs/{filename}'
        song.status = 'completed'
        song.save(update_fields=['audio_file', 'status'])
        
        logger.info(f"[TASK] Song {song_id} generated successfully")
        
        return {'status': 'success', 'song_id': song_id}
        
    except Exception as e:
        logger.error(f"[TASK] Error generating song {song_id}: {e}", exc_info=True)
        
        # Update song status
        try:
            song = Song.objects.get(id=song_id)
            song.status = 'failed'
            song.error_message = str(e)
            song.save(update_fields=['status', 'error_message'])
        except Exception as save_error:
            logger.error(f"[TASK] Failed to update song status: {save_error}")
        
        raise


def generate_song_task(song_id):
    """
    Submit a song generation task to run in the background.
    
    Args:
        song_id: ID of the Song object
        
    Returns:
        bool: True if task was submitted successfully
    """
    task_id = f"song_{song_id}"
    success = submit_background_task(task_id, _generate_song_worker, song_id)
    
    if success:
        logger.info(f"Song generation task {task_id} submitted successfully")
    else:
        logger.error(f"Failed to submit song generation task {task_id}")
    
    return success


def _generate_lyrics_worker(prompt, api_key=None, temperature=0.8):
    """
    Worker function to generate lyrics.
    Runs in a background thread.
    """
    from .generator import get_lyrics_generator
    
    try:
        logger.info(f"[TASK] Generating lyrics with prompt: {prompt[:50]}...")
        lyrics_gen = get_lyrics_generator(api_key=api_key)
        lyrics = lyrics_gen.generate(prompt, temperature=temperature)
        logger.info(f"[TASK] Lyrics generated successfully")
        return {'status': 'success', 'lyrics': lyrics}
    except Exception as e:
        logger.error(f"[TASK] Error generating lyrics: {e}", exc_info=True)
        return {'status': 'error', 'message': str(e)}


def generate_lyrics_only_task(prompt, api_key=None, temperature=0.8):
    """
    Generate lyrics (synchronous - for API responses).
    For background tasks, this runs immediately and returns the result.
    
    Args:
        prompt: The lyrics generation prompt
        api_key: Optional OpenAI API key
        temperature: Generation temperature
        
    Returns:
        dict: Result with status and lyrics or error message
    """
    return _generate_lyrics_worker(prompt, api_key, temperature)
