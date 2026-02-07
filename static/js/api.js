// API Client for Retro Cassette Music Generator

// Utility Functions
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
            // Enhanced error logging
            if (window.debug) {
                window.debug.error('[API ERROR] Response not OK:', {
                    status: response.status,
                    statusText: response.statusText,
                    data: data
                });
            }
            
            // Better error message construction
            let errorMessage = 'Request failed';
            
            if (data.error) {
                errorMessage = data.error;
            } else if (data.message) {
                errorMessage = data.message;
            } else if (data.detail) {
                errorMessage = data.detail;
            } else if (typeof data === 'object') {
                // Handle validation errors
                const errors = [];
                for (const [field, messages] of Object.entries(data)) {
                    if (Array.isArray(messages)) {
                        errors.push(`${field}: ${messages.join(', ')}`);
                    } else {
                        errors.push(`${field}: ${messages}`);
                    }
                }
                if (errors.length > 0) {
                    errorMessage = errors.join('; ');
                }
            }
            
            throw new Error(errorMessage);
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

        // Debug logging
        if (window.debug) {
            window.debug.logRequest(config.method || 'GET', url, config.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await this.handleResponse(response);
            
            // Debug logging
            if (window.debug) {
                window.debug.logResponse(url, response.status, data);
            }
            
            return data;
        } catch (error) {
            // Debug logging
            if (window.debug) {
                window.debug.error(`Request failed: ${url}`, error);
            }
            throw error;
        }
    }

    // Auth endpoints
    async register(username, email, password, password_confirm) {
        if (window.debug) {
            window.debug.log('[API REGISTER] Preparing registration request:', {
                username,
                email,
                hasPassword: !!password,
                hasPasswordConfirm: !!password_confirm
            });
        }
        
        const data = await this.request('/auth/register/', {
            method: 'POST',
            body: JSON.stringify({ username, email, password, password_confirm }),
            auth: false,
        });

        if (window.debug) {
            window.debug.log('[API REGISTER] Registration response received:', {
                hasUser: !!data.user,
                hasAccess: !!data.access,
                hasRefresh: !!data.refresh
            });
        }

        if (data.access) {
            this.setToken(data.access);
            localStorage.setItem('refresh_token', data.refresh);
            if (window.debug) {
                window.debug.log('[API REGISTER] Tokens stored successfully');
            }
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

    async setLLMSettings(data) {
        return this.request('/auth/api-key/', {
            method: 'PATCH',
            body: JSON.stringify(data),
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
    async generateLyrics(prompt, instructions = '', temperature = 0.8) {
        const requestBody = { prompt, temperature };
        if (instructions) {
            requestBody.instructions = instructions;
        }
        
        if (window.debug) {
            window.debug.log('[API] generateLyrics request:', requestBody);
        }
        
        const result = await this.request('/generation/lyrics/', {
            method: 'POST',
            body: JSON.stringify(requestBody),
        });
        
        if (window.debug) {
            window.debug.log('[API] generateLyrics response:', result);
        }
        
        return result;
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
