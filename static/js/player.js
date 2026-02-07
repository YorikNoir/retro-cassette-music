// Music Player

class Player {
    constructor() {
        this.currentSong = null;
        this.audio = null;
        this.initEventListeners();
    }

    initEventListeners() {
        const closeBtn = document.getElementById('closePlayer');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Close on background click
        const modal = document.getElementById('playerModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.close();
                }
            });
        }
    }

    async loadSong(id) {
        try {
            const song = await api.getSong(id);
            this.currentSong = song;
            
            // Record play
            if (song.audio_file) {
                api.recordPlay(id).catch(console.error);
            }
            
            this.render();
            this.show();
        } catch (error) {
            console.error('Failed to load song:', error);
            showToast('Failed to load song', 'error');
        }
    }

    render() {
        const display = document.getElementById('playerDisplay');
        if (!display || !this.currentSong) return;

        const song = this.currentSong;
        const canVote = api.isAuthenticated() && song.is_public;

        display.innerHTML = `
            <div class="player-title">${escapeHtml(song.title)}</div>
            <div class="player-meta">
                by ${escapeHtml(song.user.username)} • ${song.genre}${song.mood ? ` • ${song.mood}` : ''}
            </div>
            
            ${song.audio_file ? `
                <audio controls class="audio-player" id="audioPlayer">
                    <source src="${song.audio_file}" type="audio/wav">
                    Your browser does not support audio playback.
                </audio>
            ` : `
                <div style="text-align: center; padding: 20px; color: #666;">
                    ${song.status === 'generating' ? '⏳ Song is being generated...' : '❌ Audio not available'}
                </div>
            `}
            
            <div class="lyrics-display">
                ${escapeHtml(song.lyrics || 'No lyrics available')}
            </div>
            
            ${song.description ? `
                <div style="margin-top: 15px; padding: 10px; background: #f0f0f0; border-radius: 4px;">
                    <strong>Description:</strong> ${escapeHtml(song.description)}
                </div>
            ` : ''}
            
            <div class="player-stats">
                <div class="stat">
                    <div class="stat-icon">👍</div>
                    <div class="stat-value">${song.upvotes || 0}</div>
                    <div class="stat-label">Upvotes</div>
                </div>
                <div class="stat">
                    <div class="stat-icon">👎</div>
                    <div class="stat-value">${song.downvotes || 0}</div>
                    <div class="stat-label">Downvotes</div>
                </div>
                <div class="stat">
                    <div class="stat-icon">▶️</div>
                    <div class="stat-value">${song.play_count || 0}</div>
                    <div class="stat-label">Plays</div>
                </div>
            </div>
            
            ${canVote ? `
                <div class="player-controls">
                    <button class="vote-btn ${song.user_vote === 'up' ? 'active' : ''}" id="upvoteBtn">
                        👍 Upvote
                    </button>
                    <button class="vote-btn ${song.user_vote === 'down' ? 'active' : ''}" id="downvoteBtn">
                        👎 Downvote
                    </button>
                </div>
            ` : ''}
        `;

        // Attach vote listeners
        if (canVote) {
            const upvoteBtn = document.getElementById('upvoteBtn');
            const downvoteBtn = document.getElementById('downvoteBtn');

            if (upvoteBtn) {
                upvoteBtn.addEventListener('click', () => this.vote('up'));
            }

            if (downvoteBtn) {
                downvoteBtn.addEventListener('click', () => this.vote('down'));
            }
        }

        // Setup audio player
        const audio = document.getElementById('audioPlayer');
        if (audio) {
            this.audio = audio;
            audio.volume = 0.7;
        }
    }

    async vote(voteType) {
        if (!this.currentSong) return;

        try {
            const currentVote = this.currentSong.user_vote;
            
            if (currentVote === voteType) {
                // Remove vote
                await api.removeVote(this.currentSong.id);
                showToast('Vote removed', 'success');
            } else {
                // Add or change vote
                await api.voteSong(this.currentSong.id, voteType);
                showToast('Vote recorded', 'success');
            }

            // Reload song data
            await this.loadSong(this.currentSong.id);
        } catch (error) {
            console.error('Vote error:', error);
            showToast('Failed to record vote', 'error');
        }
    }

    show() {
        const modal = document.getElementById('playerModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    close() {
        const modal = document.getElementById('playerModal');
        if (modal) {
            modal.classList.add('hidden');
        }

        // Stop audio
        if (this.audio) {
            this.audio.pause();
            this.audio.currentTime = 0;
        }
    }
}

// Initialize player
window.player = new Player();
