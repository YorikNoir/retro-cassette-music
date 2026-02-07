// Songs Management

class SongsManager {
    constructor() {
        this.currentView = 'my';
        this.currentFilters = {};
        this.songs = [];
        
        this.initEventListeners();
    }

    initEventListeners() {
        // Create button
        const createBtn = document.getElementById('createSongBtn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.showCreateScreen());
        }

        // Back button
        const backBtn = document.getElementById('backToDashboard');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showDashboard());
        }

        // View toggle
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchView(btn.dataset.view));
        });

        // Filters
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(() => this.applyFilters(), 300));
        }

        const genreFilter = document.getElementById('genreFilter');
        if (genreFilter) {
            genreFilter.addEventListener('change', () => this.applyFilters());
        }

        const sortBy = document.getElementById('sortBy');
        if (sortBy) {
            sortBy.addEventListener('change', () => this.applyFilters());
        }

        // Create form
        const createForm = document.getElementById('createSongForm');
        if (createForm) {
            createForm.addEventListener('submit', (e) => this.handleCreateSong(e));
        }

        // Generate lyrics button
        const genLyricsBtn = document.getElementById('generateLyricsBtn');
        if (genLyricsBtn) {
            genLyricsBtn.addEventListener('click', () => this.generateLyrics());
        }
    }

    showCreateScreen() {
        document.getElementById('dashboardScreen').classList.add('hidden');
        document.getElementById('createScreen').classList.remove('hidden');
    }

    showDashboard() {
        document.getElementById('createScreen').classList.add('hidden');
        document.getElementById('dashboardScreen').classList.remove('hidden');
        this.loadSongs();
    }

    switchView(view) {
        this.currentView = view;
        
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });

        this.loadSongs();
    }

    async loadSongs() {
        try {
            const params = {
                ...this.currentFilters,
                ordering: document.getElementById('sortBy')?.value || '-created_at',
            };

            if (this.currentView === 'my') {
                params.my_songs = 'true';
            }

            const data = await api.getSongs(params);
            this.songs = data.results || data;
            this.renderSongs();
        } catch (error) {
            console.error('Failed to load songs:', error);
            showToast('Failed to load songs', 'error');
        }
    }

    applyFilters() {
        const search = document.getElementById('searchInput')?.value;
        const genre = document.getElementById('genreFilter')?.value;

        this.currentFilters = {};
        
        if (search) {
            this.currentFilters.search = search;
        }
        
        if (genre) {
            this.currentFilters.genre = genre;
        }

        this.loadSongs();
    }

    renderSongs() {
        const grid = document.getElementById('songsGrid');
        if (!grid) return;

        if (this.songs.length === 0) {
            grid.innerHTML = '<p style="text-align: center; color: var(--text-secondary); grid-column: 1/-1;">No songs found</p>';
            return;
        }

        grid.innerHTML = this.songs.map(song => this.createSongCard(song)).join('');

        // Attach event listeners
        this.songs.forEach(song => {
            const card = document.getElementById(`song-${song.id}`);
            if (card) {
                card.querySelector('.cassette-label').addEventListener('click', () => {
                    window.player.loadSong(song.id);
                });

                if (this.currentView === 'my') {
                    const publishBtn = card.querySelector('.publish-btn');
                    if (publishBtn) {
                        publishBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            this.togglePublish(song.id, song.is_public);
                        });
                    }

                    const deleteBtn = card.querySelector('.delete-btn');
                    if (deleteBtn) {
                        deleteBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            this.deleteSong(song.id);
                        });
                    }
                }
            }
        });
    }

    createSongCard(song) {
        const statusClass = song.status || 'completed';
        
        return `
            <div class="song-cassette" id="song-${song.id}">
                <div class="song-status ${statusClass}">${statusClass}</div>
                <div class="cassette-label">
                    <div class="song-title">${escapeHtml(song.title)}</div>
                    <div class="song-meta">
                        ${song.genre} ${song.mood ? `• ${song.mood}` : ''} • ${song.duration}s
                    </div>
                    <div class="song-description">
                        ${escapeHtml(song.description || song.lyrics?.substring(0, 100) || '')}
                    </div>
                </div>
                <div class="cassette-reels">
                    <div class="reel"></div>
                    <div class="reel"></div>
                </div>
                ${this.currentView === 'my' ? `
                    <div class="song-actions">
                        <button class="action-btn publish-btn">
                            ${song.is_public ? '🔒 Unpublish' : '🌐 Publish'}
                        </button>
                        <button class="action-btn delete-btn">🗑️ Delete</button>
                    </div>
                ` : `
                    <div class="song-meta" style="text-align: center; margin-top: 10px; color: var(--cassette-beige);">
                        👍 ${song.upvotes || 0} • 👎 ${song.downvotes || 0} • ▶️ ${song.play_count || 0}
                    </div>
                `}
            </div>
        `;
    }

    async handleCreateSong(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        const songData = {
            title: formData.get('title'),
            lyrics: formData.get('lyrics'),
            description: formData.get('description'),
            genre: formData.get('genre'),
            mood: formData.get('mood'),
            duration: parseInt(formData.get('duration')),
            temperature: 1.0,
        };

        try {
            showLoading(form.querySelector('button[type="submit"]'), true);
            
            const song = await api.createSong(songData);
            
            showToast('Song creation started! This may take a few minutes.', 'success');
            
            form.reset();
            this.showDashboard();
            
            // Poll for completion
            this.pollSongStatus(song.id);
        } catch (error) {
            showToast(error.message || 'Failed to create song', 'error');
        } finally {
            showLoading(form.querySelector('button[type="submit"]'), false);
        }
    }

    async generateLyrics() {
        const form = document.getElementById('createSongForm');
        const title = form.querySelector('[name="title"]').value;
        const genre = form.querySelector('[name="genre"]').value;
        const mood = form.querySelector('[name="mood"]').value;
        const instructions = form.querySelector('[name="lyrics_instructions"]').value;
        const lyricsTextarea = form.querySelector('[name="lyrics"]');
        const btn = document.getElementById('generateLyricsBtn');

        if (!title) {
            showToast('Please enter a song title first', 'error');
            return;
        }

        const prompt = `Write song lyrics for a ${genre} song titled "${title}"${mood ? ` with a ${mood} mood` : ''}.`;

        try {
            showLoading(btn, true);
            
            if (window.debug) {
                window.debug.log('[LYRICS] Sending request:', { prompt, instructions });
            }
            
            const result = await api.generateLyrics(prompt, instructions);
            
            if (window.debug) {
                window.debug.log('[LYRICS] Received response:', result);
            }
            
            if (result && result.status === 'success' && result.lyrics) {
                lyricsTextarea.value = result.lyrics;
                showToast('Lyrics generated successfully!', 'success');
            } else {
                throw new Error(result?.message || 'No lyrics returned');
            }
        } catch (error) {
            if (window.debug) {
                window.debug.error('[LYRICS] Error:', error);
            }
            showToast(error.message || 'Failed to generate lyrics', 'error');
        } finally {
            showLoading(btn, false);
        }
    }

    async togglePublish(id, isPublic) {
        try {
            const action = isPublic ? 'unpublish' : 'publish';
            await api.publishSong(id, action);
            showToast(`Song ${action}ed successfully`, 'success');
            this.loadSongs();
        } catch (error) {
            showToast(error.message || 'Failed to update song', 'error');
        }
    }

    async deleteSong(id) {
        if (!confirm('Are you sure you want to delete this song?')) {
            return;
        }

        try {
            await api.deleteSong(id);
            showToast('Song deleted successfully', 'success');
            this.loadSongs();
        } catch (error) {
            showToast(error.message || 'Failed to delete song', 'error');
        }
    }

    async pollSongStatus(id, attempts = 0) {
        if (attempts > 60) return; // Stop after 5 minutes

        try {
            const song = await api.getSong(id);
            
            if (song.status === 'completed') {
                showToast('Song generated successfully!', 'success');
                this.loadSongs();
            } else if (song.status === 'failed') {
                showToast(`Song generation failed: ${song.error_message}`, 'error');
                this.loadSongs();
            } else {
                setTimeout(() => this.pollSongStatus(id, attempts + 1), 5000);
            }
        } catch (error) {
            console.error('Failed to poll song status:', error);
        }
    }
}

// Initialize songs manager
window.songsManager = new SongsManager();
