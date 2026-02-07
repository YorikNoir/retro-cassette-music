# Retro Cassette Music Generator

A retro-themed music generation platform powered by ACE-Step AI, featuring a nostalgic cassette player interface.

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

## Installation

### Prerequisites

- Python 3.10+
- GPU with CUDA support (recommended)
- 16GB+ RAM

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd retro-cassette-music
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Download AI models:
```bash
python manage.py download_models
```

8. Run the development server:
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to start creating music!

## Project Structure

```
retro-cassette-music/
├── manage.py
├── requirements.txt
├── .env.example
├── config/                 # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # User authentication
│   ├── songs/             # Song creation & management
│   ├── library/           # User music library
│   └── generation/        # AI model integration
├── static/
│   ├── css/              # Retro cassette styles
│   ├── js/               # Frontend logic
│   └── images/           # UI assets
├── templates/            # HTML templates
└── media/               # User-generated songs
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

## License

MIT License - see LICENSE file

## Credits

Built on top of [ACE-Step](https://github.com/your-acestep-repo) - Advanced Audio Generation Model
