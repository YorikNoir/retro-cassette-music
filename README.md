# Retro Cassette Music Generator

A retro-themed music generation platform powered by ACE-Step AI, featuring a nostalgic cassette player interface.

📄 **[Technical Setup Documentation](https://yoriknoir.github.io/retro-cassette-music/Technical_Setup_Documentation.html)** - Quick reference guide for developers

## Features

- 🎵 **AI Music Generation**: Create songs using ACE-Step v1.5
- 📝 **Lyrics Generation**: Built-in LLM or use your own OpenAI API key
- 🎨 **Retro Cassette Theme**: Nostalgic 80s/90s cassette player UI
- 👤 **User Accounts**: Personalized music library per user
- ⭐ **Social Features**: Upvote, downvote, and publish your creations
- 🔍 **Filtering & Search**: Find songs by genre, mood, duration, and more
- 🔒 **Secure**: Encrypted API key storage

## Tech Stack

- **Backend**: Django 5.0+
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **AI Models**: ACE-Step v1.5, Qwen3 Embedding
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Django Auth + JWT

## Quick Start

### Prerequisites

- Python 3.10+
- Redis (for Celery task queue)
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
├── Technical_Setup_Documentation.html  # Quick reference
├── config/                        # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── celery.py                  # Celery configuration
├── apps/
│   ├── accounts/                  # User authentication
│   ├── songs/                     # Song CRUD & voting
│   ├── library/                   # User music library
│   └── generation/                # AI generation tasks
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

### Environment Variables

Key settings in `.env`:

- `SECRET_KEY` - Django secret key
- `ENCRYPTION_KEY` - **Required!** Fernet key for encrypted fields
- `DEBUG` - Enable/disable debug mode
- `MODELS_PATH` - Path to ACE-Step model files
- `CELERY_BROKER_URL` - Redis connection (default: `redis://localhost:6379/0`)
- `OPENAI_API_KEY` - Optional: for default lyrics generation

## License

MIT License - see LICENSE file

## Credits

Built on top of [ACE-Step](https://github.com/your-acestep-repo) - Advanced Audio Generation Model
