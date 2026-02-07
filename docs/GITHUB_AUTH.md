# GitHub Authentication Setup Guide

Your Git is configured with:
- **Username:** QuackAstra
- **Email:** schwarz.yorik+github@gmail.com

## Option 1: Personal Access Token (Recommended)

Since GitHub has deprecated password authentication, you need to use a Personal Access Token (PAT).

### Steps to create a PAT:

1. **Go to GitHub Settings:**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub → Your Profile → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)

2. **Generate New Token:**
   - Click "Generate new token" → "Generate new token (classic)"
   - Give it a name: `retro-cassette-music`
   - Set expiration: 90 days (or longer)
   - Select scopes:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (if using GitHub Actions)

3. **Copy the Token:**
   - GitHub will show you the token ONCE
   - Copy it immediately (you won't see it again!)

4. **Use Token When Pushing:**
   ```powershell
   git push -u origin main
   ```
   - When prompted for username: enter `YorikNoir`
   - When prompted for password: **paste your PAT token** (not your GitHub password)

### Store Credentials (so you don't need to enter it every time):

```powershell
git config --global credential.helper wincred
```

Then push again, and Windows will save your credentials securely.

## Option 2: GitHub CLI (Alternative)

Install GitHub CLI and authenticate:

```powershell
# Install GitHub CLI
winget install --id GitHub.cli

# Authenticate
gh auth login
```

## Option 3: SSH Keys (Most Secure)

1. **Generate SSH Key:**
   ```powershell
   ssh-keygen -t ed25519 -C "schwarz.yorik+github@gmail.com"
   ```

2. **Add to SSH Agent:**
   ```powershell
   Get-Service ssh-agent | Set-Service -StartupType Automatic
   Start-Service ssh-agent
   ssh-add ~\.ssh\id_ed25519
   ```

3. **Add Public Key to GitHub:**
   - Copy your public key:
     ```powershell
     cat ~\.ssh\id_ed25519.pub | clip
     ```
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste the key

4. **Change Remote to SSH:**
   ```powershell
   git remote set-url origin git@github.com:YorikNoir/retro-cassette-music.git
   ```

## Quick Test

After setting up authentication, test with:

```powershell
cd D:\Projects\stepACE-Step-1.5\retro-cassette-music
git push -u origin main
```

## Common Issues

**Error: "Support for password authentication was removed"**
→ Use a Personal Access Token instead of your password

**Error: "Permission denied"**
→ Make sure you have write access to the repository YorikNoir/retro-cassette-music

**Error: "Could not read from remote repository"**
→ Check that the repository exists and you have access
