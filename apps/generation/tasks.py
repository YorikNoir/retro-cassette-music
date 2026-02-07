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
        
        # Use -1.0 for automatic duration (let ACE-Step decide based on lyrics)
        duration_param = song.duration if song.duration else -1.0
        
        generation_result = music_gen.generate(
            lyrics=song.lyrics,
            genre=song.genre,
            mood=song.mood or '',
            duration=duration_param,
            temperature=song.temperature,
            description=song.description or ''
        )
        
        # Handle both dict and string responses (backwards compatibility)
        if isinstance(generation_result, dict):
            audio_data = generation_result.get('file')
            actual_duration = generation_result.get('duration')
        else:
            audio_data = generation_result
            actual_duration = None
        
        # Generate proper filename: "Creator - ## - Title.mp3"
        # Count user's existing songs for sequential number
        from apps.songs.models import Song
        user_song_count = Song.objects.filter(user=song.user).count()
        song_number = str(user_song_count).zfill(2)  # Zero-padded (01, 02, etc.)
        
        # Sanitize title for filename
        import re
        safe_title = re.sub(r'[<>:"/\\|?*]', '', song.title)  # Remove invalid chars
        safe_title = safe_title.strip()[:100]  # Limit length
        
        # Get username
        username = song.user.username
        
        # Create filename
        filename = f"{username} - {song_number} - {safe_title}.mp3"
        filepath = os.path.join(settings.MEDIA_ROOT, 'songs', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write audio
        import soundfile as sf
        import numpy as np
        if isinstance(audio_data, np.ndarray):
            # Save as temporary WAV first
            import tempfile
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav.close()
            sf.write(temp_wav.name, audio_data, samplerate=48000)
            
            # Convert to MP3
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(temp_wav.name)
                audio.export(filepath, format='mp3', bitrate='192k')
                os.unlink(temp_wav.name)  # Clean up temp WAV
            except ImportError:
                # Fallback: use WAV if pydub not available
                import shutil
                shutil.move(temp_wav.name, filepath)
        else:
            # If audio_data is already a path (from generator.py)
            import shutil
            shutil.move(audio_data, filepath)
        
        # Update song
        song.audio_file = f'songs/{filename}'
        song.status = 'completed'
        
        # Store actual duration if it was generated automatically
        if actual_duration and not song.duration:
            song.duration = actual_duration
            song.save(update_fields=['audio_file', 'status', 'duration'])
        else:
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
