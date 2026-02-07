# Smart Home AI Music Generator

> **A production-ready AI music generation platform designed for smart home integration, featuring multi-provider LLM support, voice command capabilities, and room-based playlist management.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

📄 **[Technical Documentation](https://htmlpreview.github.io/?https://github.com/YorikNoir/retro-cassette-music/blob/main/docs/Technical_Setup_Documentation.html)** | 🏠 **[Home Assistant Integration](https://htmlpreview.github.io/?https://github.com/YorikNoir/retro-cassette-music/blob/main/docs/HomeAssistant_Integration_Guide.html)**

---

## 🎯 Project Overview

This application is a **full-stack AI music generation platform** built with Django and PyTorch, designed to integrate seamlessly with **Home Assistant smart home systems**. It enables users to generate personalized music through voice commands, manage room-specific playlists, and stream AI-generated songs directly to smart speakers throughout their home.

### **Key Differentiators**

- **Smart Home Ready**: RESTful API endpoints for Home Assistant automation and voice command integration
- **Multi-Provider LLM Architecture**: Flexible lyrics generation supporting Local (Ollama), OpenAI, Comet API, and custom endpoints
- **Privacy-First Design**: Full offline operation with local LLM option (Llama 3.2) - no external API calls required
- **Production-Grade Security**: Fernet encryption for API keys, JWT authentication, CSRF protection
- **Background Processing**: Efficient async task manager for music & lyrics generation with configurable concurrency
- **Retro-Modern UX**: Nostalgic cassette player interface optimized for both web and smart mirror displays

---

## 🏗️ Architecture & Tech Stack

### **Backend**
- **Framework**: Django 5.0.1 + Django REST Framework 3.14.0
- **Async Processing**: Built-in background task manager for music & lyrics generation (concurrent task support)
- **AI/ML**: PyTorch 2.7.1 (CUDA 12.8), Transformers 4.57, ACE-Step v1.5 (music generation), Qwen3 Embedding
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
- **File Storage**: Local media storage with S3-compatible backend support
- **Monitoring**: Django Debug Toolbar, task status API endpoints

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
Background task → LLM lyrics + ACE-Step music generation
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

![Den Smart Mirror - Room Control](images/den_smart_mirror.webp)
*Smart mirror control interface in den: per-room playlist management and speaker selection*

![Bathroom Smart Mirror - Shower Karaoke Mode](images/bathroom_smart_display.webp)
*Smart mirror in action: 7" display showing scrolling karaoke lyrics during morning shower routine*

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

![Create New Song Interface](images/Create%20New%20Song.webp)
*Song creation interface with genre/mood selection and real-time generation progress*

### **User Management & Social**
- 👤 **Multi-User Accounts**: Separate libraries, preferences, and LLM provider settings per user
- ⭐ **Voting System**: Upvote/downvote songs, discover community favorites
- 📢 **Publishing**: Private-by-default with optional public sharing
- 📊 **Statistics**: Track songs created, published count, community engagement

![Cassette Collection - Song Library](images/Cassette%20Collection.webp)
*Retro cassette player UI with full song library, voting, and playlist management*

### **Smart Home Integration**
- 🏠 **Home Assistant API**: RESTful endpoints for automation workflows
- 🗣️ **Voice Commands**: Parse natural language to song parameters ("relaxing jazz")
- 🔊 **Room Zones**: Per-room playlists with independent speaker control
- 🎉 **Party Mode**: Synchronized multi-room playback across smart home

### **Developer-Friendly**
- 🔧 **One-Command Setup**: `scripts/setup.bat` / `scripts/setup.sh` handles venv, dependencies, migrations
- 📚 **Comprehensive Docs**: Technical architecture, API reference, deployment guide
- 🔐 **Security Best Practices**: CSRF, CORS, JWT, encrypted fields, input validation
- 🧪 **Testable**: Django test suite, API testing with Postman collections

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (tested on 3.10, 3.11, 3.12)
- **16GB+ RAM** (8GB minimum for CPU-only inference)
- **GPU with CUDA 12.8 support** (optional, recommended for 10x faster generation)
- **10GB free disk space** (for PyTorch + ACE-Step models)

### One-Command Installation

**Windows:**
```powershell
# Clone PARENT repository (includes ACE-Step models)
git clone https://github.com/YorikNoir/stepACE-Step-1.5.git
cd stepACE-Step-1.5\retro-cassette-music

# Setup (installs ACE-Step + Django dependencies, runs migrations)
scripts/setup.bat

# Start Django development server
scripts/start.bat

# Visit http://localhost:7777
```

**Linux/Mac:**
```bash
# Clone PARENT repository (includes ACE-Step models)
git clone https://github.com/YorikNoir/stepACE-Step-1.5.git
cd stepACE-Step-1.5/retro-cassette-music

# Setup
chmod +x scripts/setup.sh scripts/start.sh scripts/stop.sh
./scripts/setup.sh

# Start development server
./scripts/start.sh

# Visit http://localhost:7777
```

### Optional: Install Local LLM (Privacy Mode)

```bash
# Windows
scripts/install_local_llm.bat

# Linux/Mac  
chmod +x scripts/install_local_llm.sh
./scripts/install_local_llm.sh
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
stepACE-Step-1.5/                   # PARENT: AI music generation engine
├── acestep/                        # ACE-Step model inference code
│   ├── inference.py                # Model loading, generation pipeline
│   ├── acestep_v15_pipeline.py     # Transformer diffusion pipeline
│   └── ...                         # Audio processing, VAE, utilities
├── checkpoints/                    # Pre-trained AI models (3.5GB)
│   ├── acestep-v15-turbo/         # Music generation model
│   ├── acestep-5Hz-lm-1.7B/       # Language model for music
│   └── vae/                        # Audio VAE encoder/decoder
├── requirements.txt                # ACE-Step dependencies (PyTorch, transformers, etc.)
└── retro-cassette-music/           # Django web application (THIS PROJECT)
    ├── apps/                       # Django applications (modular architecture)
    │   ├── accounts/               # User auth, JWT, encrypted API keys
    │   ├── songs/                  # Song CRUD, voting, publishing
    │   ├── generation/             # LLM integration, ACE-Step wrapper, background tasks
    │   ├── library/                # Playlists, collections, room management
    │   └── homeassistant/          # Home Assistant API endpoints
    ├── config/                     # Django project configuration
    │   ├── settings.py             # Django settings, middleware, LLM config
    │   └── urls.py                 # URL routing, API endpoints
    ├── docs/                       # 📁 Documentation (guides, API docs, deployment)
    │   ├── Technical_Setup_Documentation.html
    │   ├── HomeAssistant_Integration_Guide.html
    │   ├── API.md
    │   ├── DEPLOYMENT.md
    │   ├── CONTRIBUTING.md
    │   └── GITHUB_AUTH.md
    ├── scripts/                    # 📁 Startup & installation scripts
    │   ├── setup.bat / setup.sh    # One-command setup
    │   ├── start.bat / start.sh    # Launch Django server
    │   ├── stop.bat / stop.sh      # Stop server
    │   └── install_local_llm.bat / install_local_llm.sh
    ├── static/                     # Frontend assets (CSS, JS, images)
    ├── templates/                  # HTML templates (SPA interface)
    ├── media/                      # User-generated songs (MP3 files)
    ├── images/                     # Screenshots and UI mockups
    ├── venv/                       # Virtual environment (auto-created)
    ├── requirements.txt            # Django app dependencies
    ├── manage.py                   # Django management utility
    ├── .env.example                # Environment variables template
    └── README.md                   # Project overview (this file)
```

**Dependency Structure:**
- **Parent `requirements.txt`**: ACE-Step AI engine (PyTorch 2.7.1, transformers, loguru, einops, vector-quantize-pytorch)
- **App `requirements.txt`**: Django web framework (DRF, JWT, CORS, encryption)
- **scripts/setup.bat / scripts/setup.sh**: Installs BOTH automatically in correct order

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
MAX_CONCURRENT_TASKS=3                   # Task concurrency
USE_GPU=True                             # CUDA acceleration
CUDA_VISIBLE_DEVICES=0

# Database (defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgresql://user:pass@localhost:5432/retro_music
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
- **Database Indexing**: user_id, created_at, is_published
- **Model Reuse**: ACE-Step loaded once per worker thread

### Frontend
- **Lazy Loading**: IntersectionObserver for images
- **Pagination**: 20 songs/page to limit DOM size
- **Debouncing**: Search input (300ms)
- **Zero Dependencies**: Vanilla JS reduces bundle to ~50KB

### AI Inference
- **GPU Acceleration**: CUDA support for 10x faster generation
- **Batch Processing**: Async task manager with configurable concurrency
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

### Monitoring & Diagnostics
```bash
# Django management
python manage.py migrate                 # Apply migrations
python manage.py createsuperuser         # Admin account
python manage.py shell                   # Interactive shell
python manage.py collectstatic           # Gather static files

# Ollama management (local LLM)
ollama list                              # Installed models
ollama pull llama3.2:3b                  # Download model
ollama ps                                # Running models

# GPU diagnostics (printed on startup)
# Check Django logs for CUDA availability and memory allocation
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate new `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Configure `ALLOWED_HOSTS` with domain
- [ ] Switch to PostgreSQL (`DATABASE_URL`)
- [ ] Configure CORS (`CORS_ALLOWED_ORIGINS`)
- [ ] Run `python manage.py collectstatic`
- [ ] Run `python manage.py migrate`
- [ ] Set up Gunicorn (4 workers) + Nginx reverse proxy
- [ ] Configure systemd service for Django background tasks
- [ ] Enable SSL with Let's Encrypt
- [ ] Set up monitoring (Sentry, CloudWatch, or ELK stack)

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

**Full API documentation**: `docs/API.md` or `/api/docs/` (Swagger/OpenAPI)

---

## 🤝 Contributing

This project follows industry best practices:
- **Code Style**: PEP 8, Black formatting, type hints
- **Git Workflow**: Feature branches, meaningful commits, PR reviews
- **Testing**: Unit tests for models/views/serializers, integration tests for workflows
- **Documentation**: Docstrings (Google style), README, Technical docs

---

## ⚡ Performance & Scalability

### Generation Times
- **Lyrics Generation**: 1-6s (Local Ollama) to 2-5s (Cloud LLMs)
- **Music Generation**: 15-30s on NVIDIA GPU, 2-5min on CPU
- **Total Time**: 20-40s typical for complete song on GPU
- **Concurrent Tasks**: Up to 3 simultaneous generations (configurable)

### Storage
- **Models**: ~3.5GB (ACE-Step + Qwen3 Embedding)
- **Per Song**: ~2-5MB (MP3 format, 192kbps)
- **Typical Deployment**: 50-100GB media storage for 10k+ songs

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🎓 Learning Outcomes & Skills Demonstrated

This project showcases expertise in:
- **Full-Stack Development**: Django backend + Vanilla JS frontend SPA
- **AI/ML Integration**: PyTorch model deployment, multi-provider LLM orchestration
- **Distributed Systems**: Background task processing, async operations
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
