# Smart Home AI Music Generator

> **A production-ready AI music generation platform designed for smart home integration, featuring multi-provider LLM support, voice command capabilities, and room-based playlist management.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

📄 **[Technical Documentation](https://htmlpreview.github.io/?https://github.com/YorikNoir/retro-cassette-music/blob/main/Technical_Setup_Documentation.html)** | 🏠 **[Home Assistant Integration](https://htmlpreview.github.io/?https://github.com/YorikNoir/retro-cassette-music/blob/main/HomeAssistant_Integration_Guide.html)**

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
## 💡 LLM Provider Comparison

| Provider | Cost | Privacy | Quality | Latency | Best For |
|----------|------|---------|---------|---------|----------|
| **Local (Ollama)** | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 1-3s | Privacy, offline use, no API costs |
| **OpenAI** | $$-$$$ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 2-5s | Best quality, creative lyrics |
| **Comet API (Claude)** | $ | ⭐⭐ | ⭐⭐⭐⭐ | 3-6s | Anthropic models, competitive pricing |
| **Custom** | Varies | ⭐⭐⭐⭐ | Varies | Varies | LM Studio, text-gen-webui, flexibility |

**Available Models:**
- **Ollama**: llama3.2:3b (2GB), mistral (4GB), phi3 (2.3GB)
- **OpenAI**: gpt-3.5-turbo, gpt-4, gpt-4-turbo
- **Comet**: claude-sonnet-4-5 (default), claude-opus-4, claude-haiku-3-5, gpt-4o
- **Custom**: Any OpenAI-compatible API endpoint

---

## 📁 Project Structure

```
retro-cassette-music/
├── apps/                           # Django applications (modular architecture)
│   ├── accounts/                   # User auth, JWT, encrypted API keys, room permissions
│   ├── songs/                      # Song CRUD, voting system, publishing logic
│   ├── library/                    # Playlists, collections, filtering, room management
│   ├── generation/                 # Celery tasks, LLM integration, ACE-Step inference
│   └── homeassistant/              # Home Assistant API endpoints (voice commands, rooms)
├── config/                         # Project configuration
│   ├── settings.py                 # Django settings, middleware, LLM providers
│   ├── urls.py                     # URL routing, API endpoints
│   └── celery.py                   # Async task queue configuration
├── static/                         # Frontend assets
│   ├── css/                        # Retro theme + smart mirror styles
│   ├── js/                         # Vanilla JavaScript (api.js, auth.js, player.js, voice.js)
│   └── images/                     # UI assets
├── templates/                      # HTML templates
│   ├── index.html                  # Main SPA with cassette player UI
│   └── smartmirror.html            # Touchscreen-optimized interface
├── media/                          # User-generated songs (WAV/MP3)
├── setup.bat / setup.sh            # One-command initial setup
├── start.bat / start.sh            # Launch Django + Celery
├── stop.bat / stop.sh              # Stop all services
├── install_local_llm.bat/.sh       # Install Ollama + Llama 3.2
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
└── Technical_Setup_Documentation.html  # Detailed architecture docs
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# Required
ENCRYPTION_KEY=<generate_with_fernet>    # API key encryption
SECRET_KEY=<django_secret_key>           # Django security

# LLM Providers (choose one or configure multiple per user)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
# COMET_API_BASE_URL=https://api.cometapi.com/v1

# Home Assistant Integration (optional)
HA_BASE_URL=http://homeassistant.local:8123
HA_WEBHOOK_SECRET=<random_secret>
ENABLE_VOICE_COMMANDS=True
DEFAULT_ROOM=Living Room

# Performance
MAX_CONCURRENT_TASKS=3                   # Celery concurrency
USE_GPU=True                             # CUDA acceleration
CUDA_VISIBLE_DEVICES=0

# Database (defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgresql://user:pass@localhost:5432/retro_music

# Redis (for Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
```

**Generate encryption key:**
```python
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🔒 Security Features

- **Encrypted API Keys**: Fernet (AES-128-CBC) encryption for API keys stored in database
- **JWT Authentication**: Short-lived access tokens (15min) + refresh tokens (7 days)
- **CSRF Protection**: Django CSRF middleware with SameSite cookies
- **Input Validation**: DRF serializers with custom validators, SQL injection prevention
- **Home Assistant Tokens**: Bearer token authentication with room-level permissions
- **Triple-Layer API Key Protection**:
  1. Database: EncryptedCharField
  2. Serializer: `write_only=True` (never in GET responses)
  3. Override: `to_representation()` explicitly removes keys

---

## 📊 Performance Optimization

### Backend
- **Query Optimization**: `select_related()`, `prefetch_related()` for foreign keys
- **Redis Caching**: Popular songs cached (5min TTL)
- **Database Indexing**: user_id, created_at, is_published
- **Model Reuse**: ACE-Step loaded once per Celery worker

### Frontend
- **Lazy Loading**: IntersectionObserver for images
- **Pagination**: 20 songs/page to limit DOM size
- **Debouncing**: Search input (300ms)
- **Zero Dependencies**: Vanilla JS reduces bundle to ~50KB

### AI Inference
- **GPU Acceleration**: CUDA support for 10x faster generation
- **Batch Processing**: Celery async tasks with configurable concurrency
- **Model Caching**: VAE decoder cached in memory

---

## 🧪 Development

### Running Tests
```bash
python manage.py test                    # Run all tests
python manage.py test apps.accounts      # Test specific app
coverage run manage.py test              # With coverage
```

### Code Quality
```bash
black .                                  # Format code
flake8 .                                 # Lint
python manage.py check --deploy          # Deployment checks
```

### Useful Commands
```bash
# Django management
python manage.py migrate                 # Apply migrations
python manage.py createsuperuser         # Admin account
python manage.py shell                   # Interactive shell
python manage.py collectstatic           # Gather static files

# Celery monitoring
celery -A config inspect active          # Active tasks
celery -A config flower                  # Web UI (localhost:5555)
celery -A config purge                   # Clear queue

# Ollama management
ollama list                              # Installed models
ollama pull llama3.2:3b                  # Download model
ollama ps                                # Running models
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate new `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Configure `ALLOWED_HOSTS` with domain
- [ ] Switch to PostgreSQL (`DATABASE_URL`)
- [ ] Set up Redis persistence (AOF enabled)
- [ ] Configure CORS (`CORS_ALLOWED_ORIGINS`)
- [ ] Run `python manage.py collectstatic`
- [ ] Run `python manage.py migrate`
- [ ] Set up Gunicorn + Nginx
- [ ] Configure systemd services for Django + Celery
- [ ] Enable SSL with Let's Encrypt
- [ ] Set up monitoring (Sentry, Flower)

### Server Configuration

```nginx
# Nginx reverse proxy
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
}
```

---

## 📚 API Documentation

### Authentication Endpoints
```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
GET  /api/auth/profile
PUT  /api/auth/profile
```

### Song Management
```http
POST   /api/generation/lyrics        # Generate lyrics only
POST   /api/generation/music         # Generate full song
GET    /api/songs/                   # List songs (paginated)
GET    /api/songs/{id}/              # Song details
PUT    /api/songs/{id}/              # Update song
DELETE /api/songs/{id}/              # Delete song
POST   /api/songs/{id}/vote          # Upvote/downvote
POST   /api/songs/{id}/publish       # Make public
```

### Home Assistant Integration
```http
POST /api/ha/generate-song           # Generate with parameters
POST /api/ha/quick-song              # Voice command parsing
GET  /api/ha/song-status/{task_id}   # Poll generation status
GET  /api/ha/playlists/{room_id}     # Room playlists
GET  /api/ha/rooms                   # List rooms/zones
POST /api/ha/party-mode              # Multi-room sync
```

**Full API documentation**: `/api/docs/` (Swagger/OpenAPI)

---

## 🤝 Contributing

This project follows industry best practices:
- **Code Style**: PEP 8, Black formatting, type hints
- **Git Workflow**: Feature branches, meaningful commits, PR reviews
- **Testing**: Unit tests for models/views/serializers, integration tests for workflows
- **Documentation**: Docstrings (Google style), README, Technical docs

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🎓 Learning Outcomes & Skills Demonstrated

This project showcases expertise in:
- **Full-Stack Development**: Django backend + Vanilla JS frontend SPA
- **AI/ML Integration**: PyTorch model deployment, multi-provider LLM orchestration
- **Distributed Systems**: Celery task queue, Redis caching, async processing
- **Smart Home IoT**: Home Assistant REST API, voice command parsing, multi-zone control
- **Security Engineering**: Encryption, JWT, CSRF protection, input validation
- **DevOps**: Docker-ready, systemd services, Nginx reverse proxy, production deployment
- **API Design**: RESTful endpoints, OpenAPI documentation, versioning
- **Database Design**: Normalized schema, foreign keys, many-to-many relationships
- **Software Architecture**: Modular Django apps, separation of concerns, scalable design

---

## 📞 Contact

**Developer**: YorikNoir  
**GitHub**: [github.com/YorikNoir/retro-cassette-music](https://github.com/YorikNoir/retro-cassette-music)  
**Documentation**: [Technical Setup Documentation](https://htmlpreview.github.io/?https://github.com/YorikNoir/retro-cassette-music/blob/main/Technical_Setup_Documentation.html)

---

*Built with ❤️ using Django, PyTorch, and ACE-Step v1.5*
