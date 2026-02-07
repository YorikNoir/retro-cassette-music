// Main Application Logic

class App {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Check authentication
        if (api.isAuthenticated()) {
            try {
                this.currentUser = await api.getProfile();
                this.showDashboard();
                this.loadStats();
                this.populateGenreFilter();
            } catch (error) {
                console.error('Failed to load profile:', error);
                this.showAuth();
            }
        } else {
            this.showAuth();
        }

        this.updateNav();
    }

    showAuth() {
        document.getElementById('authScreen').classList.remove('hidden');
        document.getElementById('dashboardScreen').classList.add('hidden');
        document.getElementById('createScreen').classList.add('hidden');
    }

    showDashboard() {
        document.getElementById('authScreen').classList.add('hidden');
        document.getElementById('dashboardScreen').classList.remove('hidden');
        document.getElementById('createScreen').classList.add('hidden');
        
        // Load songs
        window.songsManager.loadSongs();
    }

    updateNav() {
        const nav = document.getElementById('mainNav');
        if (!nav) return;

        if (this.currentUser) {
            nav.innerHTML = `
                <span style="color: var(--text-secondary);">
                    Welcome, <strong style="color: var(--accent-primary);">${escapeHtml(this.currentUser.username)}</strong>
                </span>
                <button class="retro-btn" id="settingsBtn">⚙️ Settings</button>
                <button class="retro-btn" id="logoutBtn">🚪 Logout</button>
            `;

            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', () => this.handleLogout());
            }

            const settingsBtn = document.getElementById('settingsBtn');
            if (settingsBtn) {
                settingsBtn.addEventListener('click', () => this.showSettings());
            }
        } else {
            nav.innerHTML = '';
        }
    }

    async loadStats() {
        try {
            const stats = await api.getLibraryStats();
            this.renderStats(stats);
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    renderStats(stats) {
        const panel = document.getElementById('statsPanel');
        if (!panel) return;

        panel.innerHTML = `
            <div class="stat-card">
                <span class="stat-value">${stats.total_songs || 0}</span>
                <span class="stat-label">Total Songs</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.completed_songs || 0}</span>
                <span class="stat-label">Completed</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.published_songs || 0}</span>
                <span class="stat-label">Published</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.total_plays || 0}</span>
                <span class="stat-label">Total Plays</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">${stats.total_upvotes || 0}</span>
                <span class="stat-label">Total Upvotes</span>
            </div>
        `;
    }

    populateGenreFilter() {
        const select = document.getElementById('genreFilter');
        if (!select) return;

        const genres = [
            { value: 'pop', label: 'Pop' },
            { value: 'rock', label: 'Rock' },
            { value: 'jazz', label: 'Jazz' },
            { value: 'classical', label: 'Classical' },
            { value: 'electronic', label: 'Electronic' },
            { value: 'hiphop', label: 'Hip Hop' },
            { value: 'country', label: 'Country' },
            { value: 'rnb', label: 'R&B' },
            { value: 'blues', label: 'Blues' },
            { value: 'metal', label: 'Metal' },
            { value: 'folk', label: 'Folk' },
            { value: 'ambient', label: 'Ambient' },
            { value: 'other', label: 'Other' },
        ];

        genres.forEach(genre => {
            const option = document.createElement('option');
            option.value = genre.value;
            option.textContent = genre.label;
            select.appendChild(option);
        });
    }

    showSettings() {
        const apiKey = prompt('Enter your OpenAI API key (leave empty to use default):');
        
        if (apiKey !== null) {
            this.updateAPIKey(apiKey);
        }
    }

    async updateAPIKey(apiKey) {
        try {
            await api.setAPIKey(apiKey, !!apiKey);
            showToast('API key updated successfully', 'success');
        } catch (error) {
            showToast('Failed to update API key', 'error');
        }
    }

    async handleLogout() {
        if (confirm('Are you sure you want to logout?')) {
            await auth.logout();
        }
    }
}

// Utility Functions

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function showLoading(button, loading) {
    if (!button) return;

    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.innerHTML = '<span class="loading"></span> Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
