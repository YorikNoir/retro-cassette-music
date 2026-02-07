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
            import json
            
            client = OpenAI(api_key=self.api_key)
            
            if settings.DEBUG:
                print(f"[OPENAI] Generating lyrics with {self.model}")
            
            system_message = """You are a creative songwriter. Generate song lyrics and a style description.

IMPORTANT RULES:
1. DO NOT include the song title in the lyrics
2. Return ONLY a JSON object with this exact structure:
{
  "lyrics": "...your lyrics here...",
  "style": "...short style prompt here..."
}

The style should be a comma-separated list of descriptors like:
"party, hip-hop, pop-rap, fun, playful, energetic, cartoon vibe, group vocals, chant-along, funky bass, punchy drums, synth stabs, 110 BPM, upbeat"""
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # Validate response is not HTML (error page)
            if content and (content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html')):
                error_msg = "API returned HTML instead of lyrics. Check API key and endpoint."
                if settings.DEBUG:
                    print(f"[OPENAI] ERROR: {error_msg}")
                raise ValueError(error_msg)
            
            # Clean up markdown code fences if present
            content_clean = content.strip()
            if content_clean.startswith('```json'):
                content_clean = content_clean[7:]  # Remove ```json
            elif content_clean.startswith('```'):
                content_clean = content_clean[3:]  # Remove ```
            if content_clean.endswith('```'):
                content_clean = content_clean[:-3]  # Remove closing ```
            content_clean = content_clean.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content_clean)
                lyrics = result.get('lyrics', '').strip()
                style = result.get('style', '').strip()
                
                if settings.DEBUG:
                    print(f"[OPENAI] Generated {len(lyrics)} chars lyrics, {len(style)} chars style")
                
                return {'lyrics': lyrics, 'style': style}
            except json.JSONDecodeError:
                # Fallback: treat as plain lyrics
                if settings.DEBUG:
                    print(f"[OPENAI] Failed to parse JSON, treating as plain text")
                return {'lyrics': content_clean, 'style': ''}
        except Exception as e:
            if settings.DEBUG:
                print(f"[OPENAI] Error: {e}")
            raise
    
    def _generate_comet(self, prompt, max_length, temperature):
        """Generate lyrics using Comet API."""
        try:
            from openai import OpenAI
            import json
            
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
            
            system_message = """You are a creative songwriter. Generate song lyrics and a style description.

IMPORTANT RULES:
1. DO NOT include the song title in the lyrics
2. Return ONLY a JSON object with this exact structure:
{
  "lyrics": "...your lyrics here...",
  "style": "...short style prompt here..."
}

The style should be a comma-separated list of descriptors like:
"party, hip-hop, pop-rap, fun, playful, energetic, cartoon vibe, group vocals, chant-along, funky bass, punchy drums, synth stabs, 110 BPM, upbeat"""
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature
            )
            
            # Extract lyrics from response
            if hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
            elif isinstance(response, str):
                content = response
            else:
                # Try to get content from response
                content = str(response)
            
            # Validate response is not HTML (error page)
            if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
                error_msg = "API returned HTML instead of lyrics. Check API key and endpoint."
                if settings.DEBUG:
                    print(f"[COMET] ERROR: {error_msg}")
                    print(f"[COMET] Response preview: {content[:200]}...")
                raise ValueError(error_msg)
            
            # Clean up markdown code fences if present
            content_clean = content.strip()
            if content_clean.startswith('```json'):
                content_clean = content_clean[7:]  # Remove ```json
            elif content_clean.startswith('```'):
                content_clean = content_clean[3:]  # Remove ```
            if content_clean.endswith('```'):
                content_clean = content_clean[:-3]  # Remove closing ```
            content_clean = content_clean.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content_clean)
                lyrics = result.get('lyrics', '').strip()
                style = result.get('style', '').strip()
                
                if settings.DEBUG:
                    print(f"[COMET] Generated {len(lyrics)} chars lyrics, {len(style)} chars style")
                
                return {'lyrics': lyrics, 'style': style}
            except json.JSONDecodeError:
                # Fallback: treat as plain lyrics
                if settings.DEBUG:
                    print(f"[COMET] Failed to parse JSON, treating as plain text")
                return {'lyrics': content_clean, 'style': ''}
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
            import json
            
            # Custom provider must have a base URL
            base_url = self.base_url or 'http://localhost:8000'
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            
            if settings.DEBUG:
                print(f"[CUSTOM] Generating lyrics using {base_url}")
                print(f"[CUSTOM] Model: {self.model}")
            
            system_message = """You are a creative songwriter. Generate song lyrics and a style description.

IMPORTANT RULES:
1. DO NOT include the song title in the lyrics
2. Return ONLY a JSON object with this exact structure:
{
  "lyrics": "...your lyrics here...",
  "style": "...short style prompt here..."
}

The style should be a comma-separated list of descriptors like:
"party, hip-hop, pop-rap, fun, playful, energetic, cartoon vibe, group vocals, chant-along, funky bass, punchy drums, synth stabs, 110 BPM, upbeat"""
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            
            # Validate response is not HTML (error page)
            if content and (content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html')):
                error_msg = "API returned HTML instead of lyrics. Check API endpoint and configuration."
                if settings.DEBUG:
                    print(f"[CUSTOM] ERROR: {error_msg}")
                raise ValueError(error_msg)
            
            # Clean up markdown code fences if present
            content_clean = content.strip()
            if content_clean.startswith('```json'):
                content_clean = content_clean[7:]  # Remove ```json
            elif content_clean.startswith('```'):
                content_clean = content_clean[3:]  # Remove ```
            if content_clean.endswith('```'):
                content_clean = content_clean[:-3]  # Remove closing ```
            content_clean = content_clean.strip()
            
            # Parse JSON response
            try:
                result = json.loads(content_clean)
                lyrics = result.get('lyrics', '').strip()
                style = result.get('style', '').strip()
                
                if settings.DEBUG:
                    print(f"[CUSTOM] Generated {len(lyrics)} chars lyrics, {len(style)} chars style")
                
                return {'lyrics': lyrics, 'style': style}
            except json.JSONDecodeError:
                # Fallback: treat as plain lyrics
                if settings.DEBUG:
                    print(f"[CUSTOM] Failed to parse JSON, treating as plain text")
                return {'lyrics': content_clean, 'style': ''}
        except Exception as e:
            if settings.DEBUG:
                print(f"[CUSTOM] Error: {e}")
            raise
    
    def _generate_local(self, prompt, max_length, temperature):
        """Generate lyrics using local LLM."""
        try:
            system_prompt = """You are a creative songwriter. Generate song lyrics and a style description.

IMPORTANT RULES:
1. DO NOT include the song title in the lyrics
2. Return a JSON object with this structure:
{"lyrics": "...", "style": "..."}

The style should be descriptors like: "party, hip-hop, fun, energetic, group vocals, funky bass, 110 BPM"""
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nJSON Response:"
            
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
            response_text = raw_output.replace(full_prompt, "").strip()
            
            # Clean up markdown code fences if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            elif response_text.startswith('```'):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove closing ```
            response_text = response_text.strip()
            
            # Try to parse JSON
            import json
            try:
                result = json.loads(response_text)
                lyrics = result.get('lyrics', '').strip()
                style = result.get('style', '').strip()
                
                if settings.DEBUG:
                    print(f"[LLM] Generated {len(lyrics)} chars lyrics, {len(style)} chars style")
                
                return {'lyrics': lyrics, 'style': style}
            except json.JSONDecodeError:
                # Fallback: treat as plain lyrics
                if settings.DEBUG:
                    print(f"[LLM] Failed to parse JSON, treating as plain text")
                    print(f"[LLM] First 100 chars: '{response_text[:100]}'")
                return {'lyrics': response_text, 'style': ''}
        except Exception as e:
            if settings.DEBUG:
                print(f"Local LLM generation error: {e}")
            raise


class MusicGenerator:
    """Generate music using ACE-Step model."""
    
    def __init__(self):
        self.dit_handler = None
        self.llm_handler = None
        self._load_model()
    
    def _load_model(self):
        """Load ACE-Step model."""
        try:
            from acestep.handler import AceStepHandler
            from acestep.llm_inference import LLMHandler
            from acestep.inference import GenerationConfig
            
            if settings.DEBUG:
                print(f"[ACESTEP] Initializing ACE-Step handlers...")
            
            # Get project root and checkpoint directory
            project_root = str(settings.BASE_DIR.parent)
            checkpoint_dir = os.path.join(project_root, "checkpoints")
            
            # Initialize DiT handler
            self.dit_handler = AceStepHandler()
            if settings.DEBUG:
                print(f"[ACESTEP] Loading DiT model...")
                print(f"[ACESTEP] USE_GPU setting: {settings.USE_GPU}")
                print(f"[ACESTEP] Target device: {'cuda' if settings.USE_GPU else 'cpu'}")
            
            status_msg, ok = self.dit_handler.initialize_service(
                project_root=project_root,
                config_path="acestep-v15-turbo",
                device="cuda" if settings.USE_GPU else "cpu",
                use_flash_attention=True,
                compile_model=False,
                offload_to_cpu=False,
                offload_dit_to_cpu=False,
            )
            
            if not ok:
                raise Exception(f"DiT model failed to initialize: {status_msg}")
            
            # Verify GPU is being used
            if settings.DEBUG:
                print(f"[ACESTEP] DiT model loaded successfully")
                if hasattr(self.dit_handler, 'device'):
                    print(f"[ACESTEP] DiT handler device: {self.dit_handler.device}")
                if hasattr(self.dit_handler, 'model') and hasattr(self.dit_handler.model, 'device'):
                    print(f"[ACESTEP] DiT model device: {self.dit_handler.model.device}")
                import torch
                if torch.cuda.is_available():
                    print(f"[ACESTEP] CUDA available: Yes")
                    print(f"[ACESTEP] CUDA device: {torch.cuda.get_device_name(0)}")
                    print(f"[ACESTEP] CUDA memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
                else:
                    print(f"[ACESTEP] CUDA available: No - Running on CPU!")
            
            # Initialize LLM handler
            self.llm_handler = LLMHandler()
            if settings.DEBUG:
                print(f"[ACESTEP] Loading LLM model...")
            
            llm_status, llm_ok = self.llm_handler.initialize(
                checkpoint_dir=checkpoint_dir,
                lm_model_path="acestep-5Hz-lm-0.6B",
                backend="vllm",
                device="cuda" if settings.USE_GPU else "cpu",
                offload_to_cpu=False,
                dtype=self.dit_handler.dtype,
            )
            
            if not llm_ok:
                # LLM is optional, just warn if it fails
                if settings.DEBUG:
                    print(f"[ACESTEP] Warning: LLM model failed to load: {llm_status}")
            else:
                if settings.DEBUG:
                    print(f"[ACESTEP] LLM model loaded successfully")
            
            if settings.DEBUG:
                print(f"[ACESTEP] All handlers initialized successfully")
        except Exception as e:
            import traceback
            if settings.DEBUG:
                print(f"[ACESTEP] Failed to load ACE-Step model: {e}")
                traceback.print_exc()
            raise Exception(f"ACE-Step model failed to load: {e}")
    
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
            from acestep.inference import generate_music, GenerationParams, GenerationConfig
            import tempfile
            
            # Build caption from genre, mood, and description
            caption_parts = []
            if genre:
                caption_parts.append(f"{genre} music")
            if mood:
                caption_parts.append(f"with a {mood} mood")
            if description:
                caption_parts.append(description)
            
            caption = ", ".join(caption_parts) if caption_parts else "instrumental music"
            
            # Clean up lyrics
            lyrics_clean = lyrics.strip() if lyrics else "[Instrumental]"
            
            # Handle automatic duration: use -1.0 to let model decide based on content
            duration_param = duration if duration and duration > 0 else -1.0
            
            if settings.DEBUG:
                print(f"[ACESTEP] Generating music:")
                print(f"  Caption: {caption}")
                print(f"  Lyrics: {lyrics_clean[:100]}...")
                if duration_param == -1.0:
                    print(f"  Duration: automatic (model will decide based on lyrics)")
                else:
                    print(f"  Duration: {duration_param}s (user specified)")
            
            # Create generation parameters
            params = GenerationParams(
                task_type="text2music",
                caption=caption,
                lyrics=lyrics_clean,
                duration=duration_param,
                inference_steps=8,  # Turbo model uses 8 steps
                seed=-1,  # Random seed
            )
            
            # Create generation config
            config = GenerationConfig(
                batch_size=1,
                use_random_seed=True,
            )
            
            # Generate music
            result = generate_music(
                dit_handler=self.dit_handler,
                llm_handler=self.llm_handler,
                params=params,
                config=config,
                save_dir=None,
                progress=None
            )
            
            if not result.success:
                raise Exception(f"Generation failed: {result.error or result.status_message}")
            
            if not result.audios or len(result.audios) == 0:
                raise Exception("No audio generated")
            
            # Get audio data from first result
            audio_dict = result.audios[0]
            audio_tensor = audio_dict.get("tensor")
            sample_rate = audio_dict.get("sample_rate", 48000)
            
            if audio_tensor is None:
                raise Exception("No audio tensor in result")
            
            # Save audio to temp file as MP3
            output_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            output_file.close()  # Close to allow other processes to write
            
            # Write audio file
            import soundfile as sf
            import numpy as np
            
            # Convert tensor to numpy if needed
            if hasattr(audio_tensor, 'numpy'):
                audio_np = audio_tensor.cpu().numpy()
            else:
                audio_np = np.array(audio_tensor)
            
            # Ensure shape is (samples, channels) for soundfile
            if audio_np.ndim == 2 and audio_np.shape[0] < audio_np.shape[1]:
                # Transpose from (channels, samples) to (samples, channels)
                audio_np = audio_np.T
            elif audio_np.ndim == 1:
                # Mono audio, reshape to (samples, 1)
                audio_np = audio_np.reshape(-1, 1)
            
            # First save as WAV (temporary)
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav.close()
            sf.write(temp_wav.name, audio_np, samplerate=sample_rate)
            
            # Calculate actual audio duration
            actual_duration = audio_np.shape[0] / sample_rate
            
            # Convert WAV to MP3
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(temp_wav.name)
                audio.export(output_file.name, format='mp3', bitrate='192k')
                
                # Clean up temporary WAV file
                import os
                os.unlink(temp_wav.name)
            except ImportError:
                # Fallback: if pydub not available, return WAV and rename to mp3
                if settings.DEBUG:
                    print(f"[ACESTEP] Warning: pydub not available, saving as WAV with .mp3 extension")
                import shutil
                shutil.move(temp_wav.name, output_file.name)
            
            if settings.DEBUG:
                print(f"[ACESTEP] Music generated successfully: {output_file.name}")
                print(f"[ACESTEP] Actual duration: {actual_duration:.2f}s")
                print(f"[ACESTEP] Status: {result.status_message}")
            
            # Return both file path and actual duration
            return {'file': output_file.name, 'duration': int(actual_duration)}
            
        except Exception as e:
            import traceback
            if settings.DEBUG:
                print(f"[ACESTEP] Music generation error: {e}")
                traceback.print_exc()
            raise


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
