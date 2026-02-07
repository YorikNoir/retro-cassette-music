# Retro Cassette Music Generator

A retro-themed music generation platform powered by ACE-Step AI, featuring a nostalgic cassette player interface.

📄 **[Technical Setup Documentation](https://yoriknoir.github.io/retro-cassette-music/Technical_Setup_Documentation.html)** - Quick reference guide for developers

## Features

- 🎵 **AI Music Generation**: Create songs using ACE-Step v1.5
- 📝 **Flexible Lyrics Generation**: Choose from Local LLM (Ollama), OpenAI, Comet API, or custom providers
- 🤖 **Privacy-First LLM**: Run Llama 3.2 locally - no API keys required
- 🎨 **Retro Cassette Theme**: Nostalgic 80s/90s cassette player UI
- 👤 **User Accounts**: Personalized music library per user
- ⭐ **Social Features**: Upvote, downvote, and publish your creations
- 🔍 **Filtering & Search**: Find songs by genre, mood, duration, and more
- 🔒 **Secure**: Encrypted API key storage with Fernet encryption

## Tech Stack

- **Backend**: Django 5.0+
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **AI Models**: ACE-Step v1.5, Qwen3 Embedding
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Django Auth + JWT

## Quick Start

### Prerequisites

- Python 3.10+
- GPU with CUDA support (recommended for faster generation)
- 16GB+ RAM

### Installation & Running

**Windows:**
```bash
git clone https://github.com/YorikNoir/retro-cassette-music.git
cd retro-cassette-music
setup.bat    # One-time setup: venv, dependencies, migrations
start.bat    # Start Django + Celery (opens 2 windows)
```

**Linux/Mac:**
```bash
git clone https://github.com/YorikNoir/retro-cassette-music.git
cd retro-cassette-music
chmod +x setup.sh start.sh stop.sh
./setup.sh   # One-time setup: venv, dependencies, migrations
./start.sh   # Start Django + Celery (background process)
```

**Stop all services:**
- Windows: `stop.bat` or close the windows
- Linux/Mac: `./stop.sh` or Ctrl+C in the terminal

**Visit:** [http://localhost:8000](http://localhost:8000)

## LLM Provider Options

You can choose from multiple LLM providers for lyrics generation:

### 1. Local LLM (Ollama) - Recommended for Privacy

**Pros:** 
- 🔒 Complete privacy - runs entirely on your machine
- 💰 No API costs
- ⚡ Fast response times after initial download
- 🌐 Works offline

**Cons:**
- 📦 Requires ~2-7GB disk space per model
- 💻 Uses CPU/GPU resources
- 📥 Initial model download required

**Installation:**

```bash
# Windows
install_local_llm.bat

# Linux/Mac
chmod +x install_local_llm.sh
./install_local_llm.sh
```

**Available Models:**
- `llama3.2:3b` (2GB) - Default, fast and efficient
- `mistral` (4GB) - Better creative writing
- `phi3` (2.3GB) - Microsoft's efficient model

### 2. OpenAI API

**Pros:**
- 🎯 High-quality outputs (GPT-4, GPT-3.5)
- 🚀 No local resources needed
- 📝 Excellent at creative writing

**Cons:**
- 💳 Pay-per-use API costs
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
