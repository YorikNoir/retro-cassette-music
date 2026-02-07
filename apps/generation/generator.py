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


class LyricsGenerator:
    """Generate song lyrics using LLM."""
    
    def __init__(self, provider=None, api_key=None, base_url=None, model=None):
        """Initialize lyrics generator.
        
        Args:
            provider: 'openai', 'comet', 'custom', or 'local' (default from settings)
            api_key: API key for the provider (default from settings)
            base_url: Custom base URL for API (only for custom provider)
            model: Model name to use (defaults: gpt-3.5-turbo for OpenAI, claude-sonnet-4-5 for Comet)
        """
        # Determine provider from settings or parameter
        self.provider = provider or getattr(settings, 'LLM_PROVIDER', 'local')
        self.base_url = base_url
        self.model = model
        
        # Set default models per provider if not specified
        if not self.model:
            if self.provider == 'openai':
                self.model = 'gpt-3.5-turbo'
            elif self.provider == 'comet':
                self.model = 'claude-sonnet-4-5'
            elif self.provider == 'custom':
                self.model = 'gpt-3.5-turbo'  # Default for custom providers
        
        # Get API key from settings if not provided
        if api_key is None:
            if self.provider == 'openai':
                api_key = getattr(settings, 'OPENAI_API_KEY', None)
            elif self.provider == 'comet':
                api_key = getattr(settings, 'COMET_API_KEY', None)
        
        self.api_key = api_key
        
        if settings.DEBUG:
            print(f"[LYRICS] Provider: {self.provider}")
            print(f"[LYRICS] Model: {self.model}")
            if self.base_url:
                print(f"[LYRICS] Base URL: {self.base_url}")
        
        # Load local model if using local provider
        if self.provider == 'local':
            self._load_local_model()
        elif not self.api_key:
            raise ValueError(f"API key required for provider: {self.provider}")
    
    def _load_local_model(self):
        """Load local LLM model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            model_path = os.path.join(settings.MODELS_PATH, settings.LLM_MODEL)
            
            if settings.DEBUG:
                print(f"Loading LLM from {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Ensure tokenizer has a pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                if settings.DEBUG:
                    print("Set pad_token to eos_token")
            
            # TEMPORARY: Load on CPU to avoid CUDA assertion errors
            # TODO: Fix CUDA compatibility for this model
            print("Loading LLM on CPU (CUDA disabled for LLM due to assertion errors)")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                dtype=torch.float32,
                device_map=None
            )
            self.use_cuda = False
            if settings.DEBUG:
                print("LLM loaded successfully on CPU")
        except Exception as e:
            if settings.DEBUG:
                print(f"Failed to load local LLM: {e}")
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
        if self.provider == 'openai':
            return self._generate_openai(prompt, max_length, temperature)
        elif self.provider == 'comet':
            return self._generate_comet(prompt, max_length, temperature)
        elif self.provider == 'custom':
            return self._generate_custom(prompt, max_length, temperature)
        else:
            return self._generate_local(prompt, max_length, temperature)
    
    def _generate_openai(self, prompt, max_length, temperature):
        """Generate lyrics using OpenAI API."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            if settings.DEBUG:
                print(f"[OPENAI] Generating lyrics with {self.model}")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative songwriter. Generate song lyrics based on the user's request."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature
            )
            
            lyrics = response.choices[0].message.content
            
            # Validate response is not HTML (error page)
            if lyrics and (lyrics.strip().startswith('<!DOCTYPE') or lyrics.strip().startswith('<html')):
                error_msg = "API returned HTML instead of lyrics. Check API key and endpoint."
                if settings.DEBUG:
                    print(f"[OPENAI] ERROR: {error_msg}")
                raise ValueError(error_msg)
            
            if settings.DEBUG:
                print(f"[OPENAI] Generated {len(lyrics)} chars")
            
            return lyrics.strip()
        except Exception as e:
            if settings.DEBUG:
                print(f"[OPENAI] Error: {e}")
            raise
    
    def _generate_comet(self, prompt, max_length, temperature):
        """Generate lyrics using Comet API."""
        try:
            from openai import OpenAI
            
            # Comet API uses OpenAI-compatible interface
            # OpenAI client appends /chat/completions, so base_url should be https://api.cometapi.com/v1
            base_url = getattr(settings, 'COMET_API_BASE_URL', 'https://api.cometapi.com/v1')
            client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            
            if settings.DEBUG:
                print(f"[COMET] Generating lyrics using {base_url}")
                print(f"[COMET] Model: {self.model}")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative songwriter. Generate song lyrics based on the user's request."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature
            )
            
            # Extract lyrics from response
            if hasattr(response, 'choices') and len(response.choices) > 0:
                lyrics = response.choices[0].message.content
            elif isinstance(response, str):
                lyrics = response
            else:
                # Try to get content from response
                lyrics = str(response)
            
            # Validate response is not HTML (error page)
            if lyrics.strip().startswith('<!DOCTYPE') or lyrics.strip().startswith('<html'):
                error_msg = "API returned HTML instead of lyrics. Check API key and endpoint."
                if settings.DEBUG:
                    print(f"[COMET] ERROR: {error_msg}")
                    print(f"[COMET] Response preview: {lyrics[:200]}...")
                raise ValueError(error_msg)
            
            if settings.DEBUG:
                print(f"[COMET] Generated {len(lyrics)} chars")
            
            return lyrics.strip()
        except Exception as e:
            if settings.DEBUG:
                print(f"[COMET] Error: {e}")
                import traceback
                traceback.print_exc()
            raise
    
    def _generate_custom(self, prompt, max_length, temperature):
        """Generate lyrics using custom API provider."""
        try:
            from openai import OpenAI
            
            # Custom provider must have a base URL
            base_url = self.base_url or 'http://localhost:8000'
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            
            if settings.DEBUG:
                print(f"[CUSTOM] Generating lyrics using {base_url}")
                print(f"[CUSTOM] Model: {self.model}")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative songwriter. Generate song lyrics based on the user's request."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature
            )
            
            lyrics = response.choices[0].message.content
            
            # Validate response is not HTML (error page)
            if lyrics and (lyrics.strip().startswith('<!DOCTYPE') or lyrics.strip().startswith('<html')):
                error_msg = "API returned HTML instead of lyrics. Check API endpoint and configuration."
                if settings.DEBUG:
                    print(f"[CUSTOM] ERROR: {error_msg}")
                raise ValueError(error_msg)
            
            if settings.DEBUG:
                print(f"[CUSTOM] Generated {len(lyrics)} chars")
            
            return lyrics.strip()
        except Exception as e:
            if settings.DEBUG:
                print(f"[CUSTOM] Error: {e}")
            raise
    
    def _generate_local(self, prompt, max_length, temperature):
        """Generate lyrics using local LLM."""
        try:
            system_prompt = "You are a creative songwriter. Generate song lyrics based on the user's request."
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nLyrics:"
            
            if settings.DEBUG:
                print(f"[LLM] Full prompt length: {len(full_prompt)} chars")
            
            inputs = self.tokenizer(
                full_prompt, 
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            if settings.DEBUG:
                print(f"[LLM] Generating with max_new_tokens={max_length}, temp={temperature}")
                print(f"[LLM] Input shape: {inputs['input_ids'].shape}")
            
            # Generate with adjusted parameters - suppress EOS to force generation
            with torch.no_grad():
                if settings.DEBUG:
                    print(f"[LLM] Input token IDs: {inputs['input_ids'][0].tolist()[:10]}... (first 10)")
                
                outputs = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    max_new_tokens=max_length,
                    min_new_tokens=100,  # Force at least 100 new tokens
                    temperature=temperature,
                    do_sample=True,
                    repetition_penalty=1.2,  # Stronger penalty to prevent repetition
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=None,  # Disable EOS token to prevent early stopping
                    no_repeat_ngram_size=3  # Prevent 3-gram repetition
                )
            
            if settings.DEBUG:
                print(f"[LLM] Input length: {inputs['input_ids'].shape[1]} tokens")
                print(f"[LLM] Output length: {outputs.shape[1]} tokens")
                print(f"[LLM] New tokens generated: {outputs.shape[1] - inputs['input_ids'].shape[1]}")
                print(f"[LLM] Output token IDs: {outputs[0].tolist()[:20]}... (first 20)")
                
                # Decode only the new tokens to see what they are
                new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
                print(f"[LLM] New token IDs: {new_tokens.tolist()[:20]}... (first 20 of new)")
                new_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
                print(f"[LLM] New tokens decode to: '{new_text[:200]}'")
                print(f"[LLM] New tokens decode length: {len(new_text)} chars")
            
            raw_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            if settings.DEBUG:
                print(f"[LLM] Raw output (full decode) length: {len(raw_output)} chars")
                print(f"[LLM] Raw output preview: {raw_output[:200]}")
            
            # Remove the prompt from output
            lyrics = raw_output.replace(full_prompt, "").strip()
            
            if settings.DEBUG:
                print(f"[LLM] Final lyrics length: {len(lyrics)} chars")
                print(f"[LLM] Final lyrics: {lyrics[:200] if lyrics else '(EMPTY)'}")
            
            return lyrics
        except Exception as e:
            if settings.DEBUG:
                print(f"Local LLM generation error: {e}")
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
            
            if settings.DEBUG:
                print(f"Loading ACE-Step from {model_path}")
            self.inference = AceStepInference(
                model_path=model_path,
                vae_path=vae_path,
                device="cuda" if settings.USE_GPU else "cpu"
            )
            if settings.DEBUG:
                print("ACE-Step loaded successfully")
        except Exception as e:
            if settings.DEBUG:
                print(f"Failed to load ACE-Step model: {e}")
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
            
            if settings.DEBUG:
                print("ACE-Step loaded manually")
        except Exception as e:
            if settings.DEBUG:
                print(f"Manual model loading failed: {e}")
            raise
    
    def generate(self, lyrics, genre, mood, duration, temperature=1.0, description=''):
        """
        Generate music from lyrics.
        
        Args:
            lyrics: Song lyrics
            genre: Music genre
            mood: Mood/feeling
            duration: Duration in seconds
            temperature: Sampling temperature
            description: Additional style/description for generation
        
        Returns:
            Path to generated audio file
        """
        try:
            # Prepare prompt
            mood_part = f"\nMood: {mood}" if mood else ""
            desc_part = f"\nStyle: {description}" if description else ""
            prompt = f"Genre: {genre}{mood_part}{desc_part}\nLyrics: {lyrics}"
            
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
            if settings.DEBUG:
                print(f"Music generation error: {e}")
            raise
    
    def _generate_manual(self, prompt, duration, temperature):
        """Manual generation logic."""
        # This would be implemented based on the specific ACE-Step interface
        # For now, raise not implemented
        raise NotImplementedError("Manual generation not yet implemented")


# Singleton instances
_lyrics_generator = None
_music_generator = None


def get_lyrics_generator(api_key=None, provider=None, base_url=None, model=None):
    """Get or create lyrics generator instance.
    
    Args:
        api_key: Optional API key (defaults to settings)
        provider: Optional provider override ('openai', 'comet', 'custom', 'local')
        base_url: Optional base URL for custom provider
        model: Optional model name
    """
    global _lyrics_generator
    # Create new instance if provider/key/base_url/model changes or doesn't exist
    if _lyrics_generator is None or api_key or provider or base_url or model:
        _lyrics_generator = LyricsGenerator(provider=provider, api_key=api_key, base_url=base_url, model=model)
    return _lyrics_generator


def get_music_generator():
    """Get or create music generator instance."""
    global _music_generator
    if _music_generator is None:
        _music_generator = MusicGenerator()
    return _music_generator
