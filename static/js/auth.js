// Authentication Logic

class Auth {
    constructor() {
        this.initAuthForms();
    }

    initAuthForms() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
        });

        // Login form
        const loginForm = document.getElementById('loginFormElement');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Register form
        const registerForm = document.getElementById('registerFormElement');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }
    }

    switchTab(tab) {
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tab}Form`).classList.add('active');
    }

    async handleLogin(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const username = formData.get('username');
        const password = formData.get('password');

        try {
            showLoading(form.querySelector('button[type="submit"]'), true);
            
            await api.login(username, password);
            
            showToast('Login successful!', 'success');
            
            // Load dashboard
            window.location.reload();
        } catch (error) {
            showToast(error.message || 'Login failed', 'error');
        } finally {
            showLoading(form.querySelector('button[type="submit"]'), false);
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        
        const username = formData.get('username');
        const email = formData.get('email');
        const password = formData.get('password');
        const password_confirm = formData.get('password_confirm');

        if (window.debug) {
            window.debug.log('[REGISTER] Form data collected:', {
                username,
                email,
                passwordLength: password ? password.length : 0,
                passwordConfirmLength: password_confirm ? password_confirm.length : 0,
                passwordMatch: password === password_confirm
            });
        }

        // Client-side validation
        if (username.length < 3) {
            showToast('Username must be at least 3 characters', 'error');
            return;
        }

        if (password.length < 8) {
            showToast('Password must be at least 8 characters', 'error');
            return;
        }

        if (password !== password_confirm) {
            if (window.debug) {
                window.debug.error('[REGISTER] Passwords do not match');
            }
            showToast('Passwords do not match', 'error');
            return;
        }

        try {
            showLoading(form.querySelector('button[type="submit"]'), true);
            
            if (window.debug) {
                window.debug.log('[REGISTER] Sending registration request...');
            }
            
            await api.register(username, email, password, password_confirm);
            
            if (window.debug) {
                window.debug.log('[REGISTER] Registration successful!');
            }
            
            showToast('Registration successful!', 'success');
            
            // Load dashboard
            window.location.reload();
        } catch (error) {
            if (window.debug) {
                window.debug.error('[REGISTER] Registration failed:', error);
                window.debug.error('[REGISTER] Error details:', {
                    message: error.message,
                    stack: error.stack
                });
            }
            showToast(error.message || 'Registration failed', 'error');
        } finally {
            showLoading(form.querySelector('button[type="submit"]'), false);
        }
    }

    async logout() {
        try {
            await api.logout();
            showToast('Logged out successfully', 'success');
            window.location.reload();
        } catch (error) {
            console.error('Logout error:', error);
            // Force logout even if request fails
            api.clearToken();
            window.location.reload();
        }
    }
}

// Initialize auth
const auth = new Auth();
