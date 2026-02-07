// API Client for Retro Cassette Music Generator

class API {
    constructor() {
        this.baseURL = '/api';
        this.token = localStorage.getItem('access_token');
    }

    // Set authorization token
    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    // Clear authorization token
    clearToken() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    // Get headers
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // Handle response
    async handleResponse(response) {
        if (response.status === 401) {
            // Try to refresh token
            const refreshed = await this.refreshToken();
            if (!refreshed) {
                this.clearToken();
                window.location.reload();
                throw new Error('Session expired');
            }
        }

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || data.message || 'Request failed');
        }

        return data;
    }

    // Make request
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(options.auth !== false),
        };

        const response = await fetch(url, config);
        return this.handleResponse(response);
    }

    // Auth endpoints
    async register(username, email, password, password_confirm) {
        const data = await this.request('/auth/register/', {
            method: 'POST',
            body: JSON.stringify({ username, email, password, password_confirm }),
            auth: false,
        });

        if (data.access) {
            this.setToken(data.access);
            localStorage.setItem('refresh_token', data.refresh);
        }

        return data;
    }

    async login(username, password) {
        const data = await this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
            auth: false,
        });

        if (data.access) {
            this.setToken(data.access);
            localStorage.setItem('refresh_token', data.refresh);
        }

        return data;
    }

    async logout() {
        const refresh = localStorage.getItem('refresh_token');
        if (refresh) {
            try {
                await this.request('/auth/logout/', {
                    method: 'POST',
                    body: JSON.stringify({ refresh }),
                });
            } catch (e) {
                console.error('Logout error:', e);
            }
        }
        this.clearToken();
    }

    async refreshToken() {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return false;

        try {
            const data = await this.request('/auth/token/refresh/', {
                method: 'POST',
                body: JSON.stringify({ refresh }),
                auth: false,
            });

            if (data.access) {
                this.setToken(data.access);
                return true;
            }
        } catch (e) {
            console.error('Token refresh failed:', e);
        }

        return false;
    }

    // Profile endpoints
    async getProfile() {
        return this.request('/auth/profile/');
    }

    async updateProfile(data) {
        return this.request('/auth/profile/', {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async setAPIKey(apiKey, useOwnKey) {
        return this.request('/auth/api-key/', {
            method: 'PATCH',
            body: JSON.stringify({ 
                openai_api_key: apiKey,
                use_own_api_key: useOwnKey 
            }),
        });
    }

    // Songs endpoints
    async getSongs(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/songs/?${query}`);
    }

    async getSong(id) {
        return this.request(`/songs/${id}/`);
    }

    async createSong(data) {
        return this.request('/songs/create/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async updateSong(id, data) {
        return this.request(`/songs/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    async deleteSong(id) {
        return this.request(`/songs/${id}/`, {
            method: 'DELETE',
        });
    }

    async publishSong(id, action = 'publish') {
        return this.request(`/songs/${id}/publish/`, {
            method: 'POST',
            body: JSON.stringify({ action }),
        });
    }

    async recordPlay(id) {
        return this.request(`/songs/${id}/play/`, {
            method: 'POST',
            auth: false,
        });
    }

    async voteSong(id, voteType) {
        return this.request(`/songs/${id}/vote/`, {
            method: 'POST',
            body: JSON.stringify({ vote_type: voteType }),
        });
    }

    async removeVote(id) {
        return this.request(`/songs/${id}/vote/`, {
            method: 'DELETE',
        });
    }

    // Generation endpoints
    async generateLyrics(prompt, temperature = 0.8) {
        return this.request('/generation/lyrics/', {
            method: 'POST',
            body: JSON.stringify({ prompt, temperature }),
        });
    }

    async getTaskStatus(taskId) {
        return this.request(`/generation/task/${taskId}/`);
    }

    // Library endpoints
    async getLibraryStats() {
        return this.request('/library/stats/');
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.token;
    }
}

// Create global API instance
window.api = new API();
