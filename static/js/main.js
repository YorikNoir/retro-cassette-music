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
        this.initSettingsModal();
    }

    initSettingsModal() {
        // Settings modal event listeners
        const closeSettings = document.getElementById('closeSettings');
        const cancelSettings = document.getElementById('cancelSettingsBtn');
        const saveSettings = document.getElementById('saveSettingsBtn');
        const providerSelect = document.getElementById('providerSelect');
        
        if (closeSettings) {
            closeSettings.addEventListener('click', () => this.hideSettings());
        }
        
        if (cancelSettings) {
            cancelSettings.addEventListener('click', () => this.hideSettings());
        }
        
        if (saveSettings) {
            saveSettings.addEventListener('click', () => this.saveSettings());
        }
        
        if (providerSelect) {
            providerSelect.addEventListener('change', (e) => {
                this.updateProviderUI(e.target.value);
            });
        }
        
        // Close modal when clicking outside
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideSettings();
                }
            });
        }
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
        const modal = document.getElementById('settingsModal');
        const providerSelect = document.getElementById('providerSelect');
        const apiKeyInput = document.getElementById('apiKeyInput');
        const modelInput = document.getElementById('modelInput');
        const customNameInput = document.getElementById('customNameInput');
        const customBaseUrlInput = document.getElementById('customBaseUrlInput');
        
        // Load current settings from user profile
        if (this.currentUser) {
            providerSelect.value = this.currentUser.llm_provider || 'local';
            this.updateProviderUI(providerSelect.value);
            
            // Set model if available
            if (this.currentUser.llm_model) {
                modelInput.value = this.currentUser.llm_model;
            }
            
            // SECURITY: API keys are NEVER returned from the server for security
            // The input field is always blank - user must re-enter to update
            apiKeyInput.value = '';  // Always empty - keys never exposed
            apiKeyInput.placeholder = this.currentUser.use_own_api_key ? 
                'Enter new API key to update (current key is saved)' : 
                'Enter your API key';
            
            customNameInput.value = this.currentUser.custom_provider_name || '';
            customBaseUrlInput.value = this.currentUser.custom_api_base_url || '';
        }
        
        modal.classList.remove('hidden');
    }

    hideSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.add('hidden');
    }

    updateProviderUI(provider) {
        const apiKeyGroup = document.getElementById('apiKeyGroup');
        const modelGroup = document.getElementById('modelGroup');
        const customProviderGroup = document.getElementById('customProviderGroup');
        const providerInfo = document.getElementById('providerInfo');
        const modelSelect = document.getElementById('modelInput');
        const modelHelp = document.getElementById('modelHelp');
        
        // Reset visibility
        apiKeyGroup.classList.add('hidden');
        modelGroup.classList.add('hidden');
        customProviderGroup.classList.add('hidden');
        
        const infoMessages = {
            'local': 'Using default local model for lyrics generation. No API key required.',
            'openai': 'Using OpenAI GPT models. Requires an OpenAI API key.',
            'comet': 'Using Comet API with Claude models. Requires a Comet API key.',
            'custom': 'Configure your own OpenAI-compatible API endpoint.'
        };
        
        providerInfo.innerHTML = `<p>${infoMessages[provider]}</p>`;
        
        // Update model dropdown based on provider
        modelSelect.innerHTML = '';
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        
        if (provider === 'openai') {
            apiKeyGroup.classList.remove('hidden');
            modelGroup.classList.remove('hidden');
            defaultOption.textContent = 'gpt-3.5-turbo (default)';
            modelSelect.appendChild(defaultOption);
            
            const models = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'];
            models.forEach(model => {
                const opt = document.createElement('option');
                opt.value = model;
                opt.textContent = model;
                modelSelect.appendChild(opt);
            });
            modelHelp.textContent = 'OpenAI model to use for lyrics generation';
            
        } else if (provider === 'comet') {
            apiKeyGroup.classList.remove('hidden');
            modelGroup.classList.remove('hidden');
            defaultOption.textContent = 'claude-sonnet-4-5 (default)';
            modelSelect.appendChild(defaultOption);
            
            const models = [
                'claude-sonnet-4-5',
                'claude-sonnet-3-7',
                'claude-opus-4',
                'claude-haiku-3-5',
                'gpt-4o'
            ];
            models.forEach(model => {
                const opt = document.createElement('option');
                opt.value = model;
                opt.textContent = model;
                modelSelect.appendChild(opt);
            });
            modelHelp.textContent = 'Comet API model (Claude or GPT)';
            
        } else if (provider === 'custom') {
            apiKeyGroup.classList.remove('hidden');
            modelGroup.classList.remove('hidden');
            customProviderGroup.classList.remove('hidden');
            defaultOption.textContent = 'gpt-3.5-turbo (default)';
            modelSelect.appendChild(defaultOption);
            modelHelp.textContent = 'Model name for your custom provider';
        } else {
            modelSelect.appendChild(defaultOption);
        }
    }

    async saveSettings() {
        const provider = document.getElementById('providerSelect').value;
        const apiKey = document.getElementById('apiKeyInput').value;
        const model = document.getElementById('modelInput').value;
        const customName = document.getElementById('customNameInput').value;
        const customBaseUrl = document.getElementById('customBaseUrlInput').value;
        
        // Validation - only require API key if provider needs one AND user doesn't already have one saved
        const needsApiKey = (provider === 'openai' || provider === 'comet' || provider === 'custom');
        const hasExistingKey = this.currentUser && this.currentUser.use_own_api_key && 
                                this.currentUser.llm_provider === provider;
        
        if (needsApiKey && !apiKey && !hasExistingKey) {
            showToast('API key is required for this provider', 'error');
            return;
        }
        
        if (provider === 'custom' && (!customName || !customBaseUrl)) {
            showToast('Provider name and base URL are required for custom provider', 'error');
            return;
        }
        
        try {
            await this.updateLLMSettings(provider, apiKey, model, customName, customBaseUrl);
            this.hideSettings();
            showToast('Settings saved successfully', 'success');
            
            // Reload user profile to get updated settings
            this.currentUser = await api.getProfile();
        } catch (error) {
            console.error('Failed to save settings:', error);
            showToast('Failed to save settings', 'error');
        }
    }

    async updateLLMSettings(provider, apiKey, model, customName, customBaseUrl) {
        const data = {
            llm_provider: provider,
            use_own_api_key: provider !== 'local'
        };
        
        // Only include API key if user entered a new one
        // If blank and user has existing key, backend will preserve it
        if (apiKey && apiKey.trim()) {
            data.llm_api_key = apiKey.trim();
        }
        
        if (model) {
            data.llm_model = model;
        }
        
        if (provider === 'custom') {
            data.custom_provider_name = customName;
            data.custom_api_base_url = customBaseUrl;
        }
        
        return api.setLLMSettings(data);
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
