# Deployment Guide

## Production Deployment

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- Nginx
- CUDA-capable GPU (for optimal performance)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.10 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git -y

# Install CUDA (if using GPU)
# Follow NVIDIA's official guide for your system
```

### 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql

CREATE DATABASE retro_cassette_music;
CREATE USER retrocassette WITH PASSWORD 'your-secure-password';
ALTER ROLE retrocassette SET client_encoding TO 'utf8';
ALTER ROLE retrocassette SET default_transaction_isolation TO 'read committed';
ALTER ROLE retrocassette SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE retro_cassette_music TO retrocassette;
\q
```

### 3. Application Setup

```bash
# Clone repository
cd /var/www
sudo git clone <your-repo-url> retro-cassette-music
cd retro-cassette-music

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file
cp .env.example .env
nano .env  # Edit with production settings
```

### 4. Production .env Configuration

```env
SECRET_KEY=<generate-a-secure-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_URL=postgresql://retrocassette:your-secure-password@localhost:5432/retro_cassette_music

# Models path
MODELS_PATH=../checkpoints
VAE_PATH=../checkpoints/vae

# Security
ENCRYPTION_KEY=<generate-fernet-key>

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 5. Generate Secret Keys

```python
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate Fernet encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 6. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 7. Setup Gunicorn

Create `/etc/systemd/system/retro-cassette.service`:

```ini
[Unit]
Description=Retro Cassette Music Generator
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/retro-cassette-music
Environment="PATH=/var/www/retro-cassette-music/venv/bin"
ExecStart=/var/www/retro-cassette-music/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/retro-cassette-music/retro-cassette.sock \
    --timeout 120 \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 8. Setup Celery

Create `/etc/systemd/system/retro-cassette-celery.service`:

```ini
[Unit]
Description=Retro Cassette Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/retro-cassette-music
Environment="PATH=/var/www/retro-cassette-music/venv/bin"
ExecStart=/var/www/retro-cassette-music/venv/bin/celery -A config worker \
    --loglevel=info \
    --concurrency=2

[Install]
WantedBy=multi-user.target
```

### 9. Setup Nginx

Create `/etc/nginx/sites-available/retro-cassette`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/retro-cassette-music/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/retro-cassette-music/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/retro-cassette-music/retro-cassette.sock;
        proxy_read_timeout 180s;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/retro-cassette /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. Start Services

```bash
# Start and enable services
sudo systemctl start retro-cassette
sudo systemctl enable retro-cassette

sudo systemctl start retro-cassette-celery
sudo systemctl enable retro-cassette-celery

sudo systemctl start redis
sudo systemctl enable redis
```

### 11. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 12. Download AI Models

```bash
cd /var/www
# Copy models from your development environment
# Or download using the model downloader
python manage.py download_models
```

## Monitoring

### Check Service Status

```bash
sudo systemctl status retro-cassette
sudo systemctl status retro-cassette-celery
sudo systemctl status nginx
sudo systemctl status redis
```

### View Logs

```bash
# Application logs
sudo journalctl -u retro-cassette -f

# Celery logs
sudo journalctl -u retro-cassette-celery -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Backup Strategy

### Database Backup

```bash
# Create backup script /var/backups/retro-cassette-backup.sh
#!/bin/bash
BACKUP_DIR="/var/backups/retro-cassette"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump retro_cassette_music > $BACKUP_DIR/db_$TIMESTAMP.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz /var/www/retro-cassette-music/media

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /var/backups/retro-cassette-backup.sh
```

## Scaling

### Horizontal Scaling

- Use load balancer (e.g., Nginx, HAProxy)
- Add multiple application servers
- Use shared Redis/PostgreSQL
- Store media files on S3 or shared storage

### Performance Optimization

- Use CDN for static/media files
- Enable caching (Redis)
- Optimize database queries
- Use connection pooling
- Monitor with tools like New Relic or DataDog

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable firewall (ufw)
- [ ] Disable root SSH login
- [ ] Keep system updated
- [ ] Use SSL/TLS
- [ ] Set up fail2ban
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity
