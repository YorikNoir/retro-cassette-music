# Smart Home AI Music Generator

> **A production-ready AI music generation platform designed for smart home integration, featuring multi-provider LLM support, voice command capabilities, and room-based playlist management.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

📄 **[Technical Documentation](Technical_Setup_Documentation.html)** | 🏠 **[Home Assistant Integration](#home-assistant-integration)** | 🎵 **[Live Demo](http://localhost:8000)**

---

## 🎯 Project Overview

This application is a **full-stack AI music generation platform** built with Django and PyTorch, designed to integrate seamlessly with **Home Assistant smart home systems**. It enables users to generate personalized music through voice commands, manage room-specific playlists, and stream AI-generated songs directly to smart speakers throughout their home.

### **Key Differentiators**

- **Smart Home Ready**: RESTful API endpoints for Home Assistant automation and voice command integration
- **Multi-Provider LLM Architecture**: Flexible lyrics generation supporting Local (Ollama), OpenAI, Comet API, and custom endpoints
- **Privacy-First Design**: Full offline operation with local LLM option (Llama 3.2) - no external API calls required
- **Production-Grade Security**: Fernet encryption for API keys, JWT authentication, CSRF protection
- **Scalable Task Processing**: Celery + Redis for async music generation with concurrent task management
- **Retro-Modern UX**: Nostalgic cassette player interface optimized for both web and smart mirror displays

---

## 🏗️ Architecture & Tech Stack

### **Backend**
- **Framework**: Django 5.0.1 + Django REST Framework 3.14.0
- **Task Queue**: Celery 5.3.4 with Redis broker for async processing
- **AI/ML**: PyTorch 2.10, Transformers 5.1, ACE-Step v1.5 (music generation), Qwen3 Embedding
- **Authentication**: JWT tokens (djangorestframework-simplejwt) + Home Assistant long-lived token support
- **Database**: SQLite (development), PostgreSQL-ready (production scaling)
- **Security**: Fernet symmetric encryption (django-encrypted-model-fields)

### **Frontend**
- **Stack**: Vanilla JavaScript (ES6+), HTML5, CSS3 - zero framework dependencies
- **UI/UX**: Responsive design with retro cassette theme + smart mirror interface
- **Features**: Real-time updates, audio playback, drag-drop playlist management

### **AI Models**
- **Music Generation**: ACE-Step v1.5 Turbo (Transformer-based diffusion, 5Hz latent → 44.1kHz audio)
- **Lyrics Generation**: Multi-provider support (Ollama/Llama 3.2, OpenAI GPT-3.5/4, Claude Sonnet 4)
- **Embeddings**: Qwen3-Embedding-0.6B for semantic music understanding

### **Infrastructure**
- **Deployment**: Gunicorn + Nginx reverse proxy, systemd services
- **Caching**: Redis (song metadata, user sessions)
- **File Storage**: Local media storage with S3-compatible backend support
- **Monitoring**: Celery Flower for task monitoring, Django Debug Toolbar

---

## 🏠 Home Assistant Integration

### **Voice Command Workflow**
```
User: "Hey Google, create a relaxing jazz song for the living room"
  ↓
Home Assistant captures intent → Parse voice command
  ↓
POST /api/ha/quick-song {voice_command, room_context}
  ↓
Background Celery task → LLM lyrics + ACE-Step music generation
  ↓
Poll /api/ha/song-status/{task_id} → Complete (15-30s)
  ↓
TTS announcement + Stream to room speakers → Add to room playlist
```

### **API Endpoints**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ha/generate-song` | POST | Generate song with specific parameters |
| `/api/ha/quick-song` | POST | AI-parsed voice command generation |
| `/api/ha/song-status/{id}` | GET | Poll generation progress |
| `/api/ha/playlists/{room_id}` | GET | Room-specific playlists |
| `/api/ha/rooms` | GET | List configured rooms/zones |
| `/api/ha/party-mode` | POST | Multi-room synchronized playback |

### **Room-Based Playlists**
- Separate playlists per room/zone (Living Room, Kitchen, Bedroom)
- Guest access control for temporary song creation
- Party mode: Multi-room synchronized playlist across smart speakers
- Context-aware defaults (room learns preferred genres/moods)

---

## ✨ Core Features

## ✨ Core Features

### **AI Music Generation**
- 🎵 **ACE-Step v1.5**: State-of-the-art Transformer-based diffusion model for high-quality music synthesis
- ⏱️ **15-30s Generation**: GPU-accelerated inference (RTX 3090), CPU fallback supported
- 🎼 **Multi-Genre Support**: Rock, Pop, Jazz, Electronic, Classical, Hip-Hop, Country, Ambient
- 🎹 **Parametric Control**: BPM, key signature, mood (uplifting, relaxing, energetic, melancholic)

### **Flexible Lyrics Generation**
- **4 Provider Options**: Local (Ollama), OpenAI, Comet API (Claude), Custom API
- **Privacy Mode**: Llama 3.2 3B runs entirely offline - zero external API calls
- **Model Selection**: Choose GPT-3.5/4, Claude Sonnet 4/Opus 4, or any OpenAI-compatible endpoint
- **Encrypted Storage**: API keys protected with Fernet (AES-128-CBC) encryption at rest

### **User Management & Social**
- 👤 **Multi-User Accounts**: Separate libraries, preferences, and LLM provider settings per user
- ⭐ **Voting System**: Upvote/downvote songs, discover community favorites
- 📢 **Publishing**: Private-by-default with optional public sharing
- 📊 **Statistics**: Track songs created, published count, community engagement

### **Smart Home Integration**
- 🏠 **Home Assistant API**: RESTful endpoints for automation workflows
- 🗣️ **Voice Commands**: Parse natural language to song parameters ("relaxing jazz")
- 🔊 **Room Zones**: Per-room playlists with independent speaker control
- 🎉 **Party Mode**: Synchronized multi-room playback across smart home

### **Developer-Friendly**
- 🔧 **One-Command Setup**: `setup.bat` / `setup.sh` handles venv, dependencies, migrations
- 📚 **Comprehensive Docs**: Technical architecture, API reference, deployment guide
- 🔐 **Security Best Practices**: CSRF, CORS, JWT, encrypted fields, input validation
- 🧪 **Testable**: Django test suite, API testing with Postman collections

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (tested on 3.10, 3.11)
- **16GB+ RAM** (8GB minimum for CPU-only inference)
- **GPU with CUDA support** (optional, recommended for 10x faster generation)
- **Redis 5.0+** (for Celery task queue)

### One-Command Installation

**Windows:**
```powershell
# Clone repository
git clone https://github.com/YorikNoir/retro-cassette-music.git
cd retro-cassette-music

# Setup (creates venv, installs deps, runs migrations)
setup.bat

# Start Django + Celery (opens 2 terminal windows)
start.bat

# Visit http://localhost:8000
```

**Linux/Mac:**
```bash
# Clone repository
git clone https://github.com/YorikNoir/retro-cassette-music.git
cd retro-cassette-music

# Setup
chmod +x setup.sh start.sh stop.sh
./setup.sh

# Start (background processes)
./start.sh

# Visit http://localhost:8000
```

### Optional: Install Local LLM (Privacy Mode)

```bash
# Windows
install_local_llm.bat

# Linux/Mac  
chmod +x install_local_llm.sh
./install_local_llm.sh
```

Downloads Ollama + Llama 3.2 3B (~2GB) for offline lyrics generation.

---

## 💡 LLM Provider Comparison
- 🌐 Requires internet connection
- 🔐 Data sent to OpenAI servers

**Setup:** Add your OpenAI API key in Settings → LLM Provider → OpenAI

### 3. Comet API

**Pros:**
- 🤖 Access to Claude models (Anthropic)
- 💰 Competitive pricing
- 🎨 Great for creative content

**Cons:**
- 💳 Pay-per-use API costs
- 🌐 Requires internet connection

**Setup:** Add your Comet API key in Settings → LLM Provider → Comet API
**Default Model:** claude-sonnet-4-5

### 4. Custom API Provider

Connect to any OpenAI-compatible API endpoint (e.g., local LM Studio, text-generation-webui).

### Manual Setup (Advanced)

If you prefer manual setup or need more control:

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/YorikNoir/retro-cassette-music.git
   cd retro-cassette-music
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env - IMPORTANT: Set ENCRYPTION_KEY
   # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

5. **Initialize database:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Optional: admin access
   ```

6. **Download AI models:**
   ```bash
   python manage.py download_models
   ```

7. **Start services manually:**
   ```bash
   # Terminal 1: Django server
   python manage.py runserver
   
   # Terminal 2: Celery worker
   celery -A config worker --loglevel=info --pool=solo  # Windows
   celery -A config worker --loglevel=info              # Linux/Mac
   ```

## Project Structure

```
retro-cassette-music/
├── manage.py
├── requirements.txt
├── .env.example
├── start.bat / start.sh           # Start all services
├── stop.bat / stop.sh             # Stop all services  
├── setup.bat / setup.sh           # Initial setup
├── install_local_llm.bat / .sh    # Install Ollama + Llama 3.2
├── Technical_Setup_Documentation.html  # Technical reference guide
├── config/                        # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── celery.py                  # Celery configuration
├── apps/
│   ├── accounts/                  # User authentication & LLM provider settings
│   ├── songs/                     # Song CRUD & voting
│   ├── library/                   # User music library
│   └── generation/                # AI generation tasks (Celery)
├── static/
│   ├── css/                       # Retro cassette styles
│   │   ├── main.css
│   │   └── cassette.css
│   ├── js/                        # Vanilla JavaScript
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── songs.js
│   │   └── player.js
│   └── images/                    # UI assets
├── templates/                     # HTML templates
│   └── index.html                 # Single-page app
└── media/                         # User-generated content
```

## Usage

### Creating a Song

1. Log in to your account
2. Click "Create New Song"
3. Choose to generate lyrics with AI or write your own
4. Select genre, mood, and duration
5. Click "Generate Music"
6. Listen and save to your library!

### Publishing Songs

- Songs are private by default
- Click "Publish" to share with the community
- Other users can discover and vote on published songs

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
```bash
black .
flake8 .
```

### Project Scripts

| Script | Platform | Purpose |
|--------|----------|---------|
| `setup.bat` / `setup.sh` | Win / Unix | One-time setup: venv, deps, migrations |
| `start.bat` / `start.sh` | Win / Unix | Start Django + Celery together |
| `stop.bat` / `stop.sh` | Win / Unix | Stop all services |
| `install_local_llm.bat` / `install_local_llm.sh` | Win / Unix | Install Ollama and Llama 3.2 for local lyrics generation |

### Environment Variables

Key settings in `.env`:

- `SECRET_KEY` - Django secret key (auto-generated if not set)
- `ENCRYPTION_KEY` - **Required!** Fernet key for encrypted API keys storage
  - Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `DEBUG` - Enable/disable debug mode (default: False)
- `MODELS_PATH` - Path to ACE-Step model files (default: ./checkpoints)
- `MAX_CONCURRENT_TASKS` - Number of parallel song generations (default: 3)
- `OLLAMA_BASE_URL` - Ollama API endpoint (default: http://localhost:11434)
- `OLLAMA_MODEL` - Default Ollama model (default: llama3.2:3b)

## License

MIT License - see LICENSE file

## Quick Reference

### LLM Provider Comparison

| Provider | Cost | Privacy | Quality | Models | Best For |
|----------|------|---------|---------|--------|----------|
| **Local (Ollama)** | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | llama3.2, mistral, phi3 | Privacy, offline use |
| **OpenAI** | $$ | ⭐⭐ | ⭐⭐⭐⭐⭐ | GPT-3.5, GPT-4 | Best quality |
| **Comet API** | $ | ⭐⭐ | ⭐⭐⭐⭐ | Claude models, GPT-4o | Creative content |
| **Custom** | Varies | ⭐⭐⭐⭐ | Varies | Any OpenAI-compatible | Flexibility |

### Useful Commands

```bash
# Check Ollama status
ollama list                    # List installed models
ollama ps                      # Show running models
ollama pull llama3.2:3b        # Download specific model
ollama rm mistral              # Remove model

# Django management
python manage.py migrate       # Apply database migrations
python manage.py createsuperuser  # Create admin account
python manage.py collectstatic # Gather static files
python manage.py shell         # Interactive Python shell

# Celery monitoring
celery -A config inspect active   # Show active tasks
celery -A config inspect stats    # Worker statistics
celery -A config purge            # Clear all tasks

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### API Endpoints

```
POST /api/auth/register         # Create new user
POST /api/auth/login            # Get JWT tokens
POST /api/auth/refresh          # Refresh access token
GET  /api/auth/user             # Get current user profile
PUT  /api/auth/user             # Update user settings

POST /api/songs/generate        # Generate new song
GET  /api/songs/                # List songs (paginated)
GET  /api/songs/{id}/           # Get song details
PUT  /api/songs/{id}/           # Update song
DELETE /api/songs/{id}/         # Delete song
POST /api/songs/{id}/vote       # Vote on song
POST /api/songs/{id}/publish    # Publish song
```

## Credits

Built on top of [ACE-Step](https://github.com/your-acestep-repo) - Advanced Audio Generation Model
