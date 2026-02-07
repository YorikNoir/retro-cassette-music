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

        if (password !== password_confirm) {
            showToast('Passwords do not match', 'error');
            return;
        }

        try {
            showLoading(form.querySelector('button[type="submit"]'), true);
            
            await api.register(username, email, password, password_confirm);
            
            showToast('Registration successful!', 'success');
            
            // Load dashboard
            window.location.reload();
        } catch (error) {
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
