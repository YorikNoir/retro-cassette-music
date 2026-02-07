"""
Celery tasks for async song generation.
"""
from celery import shared_task
from django.conf import settings
import logging
import os
import uuid

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_song_task(self, song_id):
    """
    Async task to generate music for a song.
    
    Args:
        song_id: ID of the Song object
    """
    from apps.songs.models import Song
    from .generator import get_lyrics_generator, get_music_generator
    
    try:
        song = Song.objects.get(id=song_id)
        logger.info(f"Starting generation for song {song_id}: {song.title}")
        
        # Update status
        song.status = 'generating'
        song.save(update_fields=['status'])
        
        # Get API key if user has their own
        api_key = None
        if song.user.use_own_api_key and song.user.openai_api_key:
            api_key = song.user.openai_api_key
        
        # Generate lyrics if needed (user might have provided their own)
        if not song.lyrics or song.lyrics.strip() == "":
            logger.info("Generating lyrics...")
            lyrics_gen = get_lyrics_generator(api_key=api_key)
            prompt = f"Write song lyrics for a {song.genre} song with a {song.mood} mood. Title: {song.title}"
            song.lyrics = lyrics_gen.generate(prompt, temperature=song.temperature)
            song.save(update_fields=['lyrics'])
        
        # Generate music
        logger.info("Generating music...")
        music_gen = get_music_generator()
        audio_data = music_gen.generate(
            lyrics=song.lyrics,
            genre=song.genre,
            mood=song.mood,
            duration=song.duration,
            temperature=song.temperature
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
        
        logger.info(f"Song {song_id} generated successfully")
        
        return {'status': 'success', 'song_id': song_id}
        
    except Exception as e:
        logger.error(f"Error generating song {song_id}: {e}", exc_info=True)
        
        # Update song status
        try:
            song = Song.objects.get(id=song_id)
            song.status = 'failed'
            song.error_message = str(e)
            song.save(update_fields=['status', 'error_message'])
        except:
            pass
        
        # Retry
        raise self.retry(exc=e, countdown=60)


@shared_task
def generate_lyrics_only_task(prompt, api_key=None, temperature=0.8):
    """
    Generate lyrics without creating a song.
    Used for preview/testing.
    """
    from .generator import get_lyrics_generator
    
    try:
        lyrics_gen = get_lyrics_generator(api_key=api_key)
        lyrics = lyrics_gen.generate(prompt, temperature=temperature)
        return {'status': 'success', 'lyrics': lyrics}
    except Exception as e:
        logger.error(f"Error generating lyrics: {e}")
        return {'status': 'error', 'message': str(e)}
