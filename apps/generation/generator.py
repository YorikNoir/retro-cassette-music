"""
AI Generation integration - LLM for lyrics and ACE-Step for audio.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import acestep modules
parent_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

from django.conf import settings
import torch
import logging

logger = logging.getLogger(__name__)


class LyricsGenerator:
    """Generate song lyrics using LLM."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.use_openai = bool(api_key)
        
        if not self.use_openai:
            # Use local LLM
            self._load_local_model()
    
    def _load_local_model(self):
        """Load local LLM model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            model_path = os.path.join(settings.MODELS_PATH, settings.LLM_MODEL)
            
            logger.info(f"Loading LLM from {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if settings.USE_GPU else torch.float32,
                device_map="auto" if settings.USE_GPU else None
            )
            logger.info("LLM loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            raise
    
    def generate(self, prompt, max_length=500, temperature=0.8):
        """
        Generate lyrics based on prompt.
        
        Args:
            prompt: Text prompt describing the song
            max_length: Maximum length of generated text
            temperature: Sampling temperature
        
        Returns:
            Generated lyrics as string
        """
        if self.use_openai:
            return self._generate_openai(prompt, max_length, temperature)
        else:
            return self._generate_local(prompt, max_length, temperature)
    
    def _generate_openai(self, prompt, max_length, temperature):
        """Generate lyrics using OpenAI API."""
        try:
            import openai
            
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative songwriter. Generate song lyrics based on the user's request."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature
            )
            
            lyrics = response.choices[0].message.content
            return lyrics.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _generate_local(self, prompt, max_length, temperature):
        """Generate lyrics using local LLM."""
        try:
            system_prompt = "You are a creative songwriter. Generate song lyrics based on the user's request."
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nLyrics:"
            
            inputs = self.tokenizer(full_prompt, return_tensors="pt")
            if settings.USE_GPU:
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            lyrics = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the prompt from output
            lyrics = lyrics.replace(full_prompt, "").strip()
            
            return lyrics
        except Exception as e:
            logger.error(f"Local LLM generation error: {e}")
            raise


class MusicGenerator:
    """Generate music using ACE-Step model."""
    
    def __init__(self):
        self._load_model()
    
    def _load_model(self):
        """Load ACE-Step model."""
        try:
            from acestep.inference import AceStepInference
            
            model_path = os.path.join(settings.MODELS_PATH, settings.ACESTEP_MODEL)
            vae_path = settings.VAE_PATH
            
            logger.info(f"Loading ACE-Step from {model_path}")
            self.inference = AceStepInference(
                model_path=model_path,
                vae_path=vae_path,
                device="cuda" if settings.USE_GPU else "cpu"
            )
            logger.info("ACE-Step loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ACE-Step model: {e}")
            # Fallback to manual loading
            self._load_model_manual()
    
    def _load_model_manual(self):
        """Manual model loading as fallback."""
        try:
            import importlib.util
            
            # Load configuration
            config_path = os.path.join(settings.MODELS_PATH, settings.ACESTEP_MODEL, 'configuration_acestep_v15.py')
            spec = importlib.util.spec_from_file_location("config", config_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            # Load model
            model_file = os.path.join(settings.MODELS_PATH, settings.ACESTEP_MODEL, 'modeling_acestep_v15_turbo.py')
            spec = importlib.util.spec_from_file_location("model", model_file)
            model_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(model_module)
            
            # Initialize
            self.model = model_module.AceStepV15Turbo.from_pretrained(
                os.path.join(settings.MODELS_PATH, settings.ACESTEP_MODEL)
            )
            
            if settings.USE_GPU:
                self.model = self.model.cuda()
            
            logger.info("ACE-Step loaded manually")
        except Exception as e:
            logger.error(f"Manual model loading failed: {e}")
            raise
    
    def generate(self, lyrics, genre, mood, duration, temperature=1.0):
        """
        Generate music from lyrics.
        
        Args:
            lyrics: Song lyrics
            genre: Music genre
            mood: Mood/feeling
            duration: Duration in seconds
            temperature: Sampling temperature
        
        Returns:
            Path to generated audio file
        """
        try:
            # Prepare prompt
            prompt = f"Genre: {genre}\nMood: {mood}\nLyrics: {lyrics}"
            
            # Generate audio
            if hasattr(self, 'inference'):
                audio = self.inference.generate(
                    prompt=prompt,
                    duration=duration,
                    temperature=temperature
                )
            else:
                # Manual generation
                audio = self._generate_manual(prompt, duration, temperature)
            
            return audio
        except Exception as e:
            logger.error(f"Music generation error: {e}")
            raise
    
    def _generate_manual(self, prompt, duration, temperature):
        """Manual generation logic."""
        # This would be implemented based on the specific ACE-Step interface
        # For now, raise not implemented
        raise NotImplementedError("Manual generation not yet implemented")


# Singleton instances
_lyrics_generator = None
_music_generator = None


def get_lyrics_generator(api_key=None):
    """Get or create lyrics generator instance."""
    global _lyrics_generator
    if _lyrics_generator is None or api_key:
        _lyrics_generator = LyricsGenerator(api_key=api_key)
    return _lyrics_generator


def get_music_generator():
    """Get or create music generator instance."""
    global _music_generator
    if _music_generator is None:
        _music_generator = MusicGenerator()
    return _music_generator
