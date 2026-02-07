// Server Status Indicator
class ServerStatus {
    constructor() {
        this.statusElement = document.getElementById('serverStatus');
        this.statusDot = this.statusElement.querySelector('.status-dot');
        this.statusText = this.statusElement.querySelector('.status-text');
        this.checkInterval = 5000; // 5 seconds
        this.isOnline = false;
        
        this.init();
    }
    
    init() {
        // Check immediately
        this.checkStatus();
        
        // Then check every 5 seconds
        setInterval(() => this.checkStatus(), this.checkInterval);
    }
    
    async checkStatus() {
        try {
            const response = await fetch('/api/', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                signal: AbortSignal.timeout(3000) // 3 second timeout
            });
            
            if (response.ok) {
                this.setOnline();
            } else {
                this.setOffline();
            }
        } catch (error) {
            this.setOffline();
        }
    }
    
    setOnline() {
        if (!this.isOnline) {
            this.isOnline = true;
            this.statusElement.classList.remove('offline');
            this.statusElement.classList.add('online');
            this.statusText.textContent = 'Server Online';
        }
    }
    
    setOffline() {
        if (this.isOnline !== false) {
            this.isOnline = false;
            this.statusElement.classList.remove('online');
            this.statusElement.classList.add('offline');
            this.statusText.textContent = 'Server Offline';
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.serverStatus = new ServerStatus();
    });
} else {
    window.serverStatus = new ServerStatus();
}
