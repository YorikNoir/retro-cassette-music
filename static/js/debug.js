// Debug Utilities for Retro Cassette Music

class Debug {
    constructor() {
        this.enabled = false;
        this.init();
    }

    init() {
        // Check if debug mode is enabled via URL parameter or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        const debugParam = urlParams.get('debug');
        const debugStorage = localStorage.getItem('debug_mode');
        
        if (debugParam === 'true' || debugParam === '1') {
            this.enable();
        } else if (debugStorage === 'true') {
            this.enabled = true;
        }
        
        this.log('Debug utility initialized', { enabled: this.enabled });
    }

    enable() {
        this.enabled = true;
        localStorage.setItem('debug_mode', 'true');
        this.log('Debug mode ENABLED', { 
            time: new Date().toISOString(),
            userAgent: navigator.userAgent 
        });
        this.showDebugIndicator();
    }

    disable() {
        this.enabled = false;
        localStorage.removeItem('debug_mode');
        this.log('Debug mode DISABLED');
        this.hideDebugIndicator();
    }

    toggle() {
        if (this.enabled) {
            this.disable();
        } else {
            this.enable();
        }
    }

    log(message, data = null) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[DEBUG ${timestamp}]`;
        
        if (data) {
            console.log(`%c${prefix} ${message}`, 'color: #00d4ff; font-weight: bold;', data);
        } else {
            console.log(`%c${prefix} ${message}`, 'color: #00d4ff; font-weight: bold;');
        }
    }

    error(message, error = null) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[ERROR ${timestamp}]`;
        
        if (error) {
            console.error(`%c${prefix} ${message}`, 'color: #e94560; font-weight: bold;', error);
        } else {
            console.error(`%c${prefix} ${message}`, 'color: #e94560; font-weight: bold;');
        }
    }

    warn(message, data = null) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[WARN ${timestamp}]`;
        
        if (data) {
            console.warn(`%c${prefix} ${message}`, 'color: #ffa07a; font-weight: bold;', data);
        } else {
            console.warn(`%c${prefix} ${message}`, 'color: #ffa07a; font-weight: bold;');
        }
    }

    info(message, data = null) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[INFO ${timestamp}]`;
        
        if (data) {
            console.info(`%c${prefix} ${message}`, 'color: #39ff14; font-weight: bold;', data);
        } else {
            console.info(`%c${prefix} ${message}`, 'color: #39ff14; font-weight: bold;');
        }
    }

    table(label, data) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toLocaleTimeString();
        console.log(`%c[TABLE ${timestamp}] ${label}`, 'color: #00d4ff; font-weight: bold;');
        console.table(data);
    }

    group(label, func) {
        if (!this.enabled) {
            func();
            return;
        }
        
        console.group(`%c[GROUP] ${label}`, 'color: #00d4ff; font-weight: bold;');
        func();
        console.groupEnd();
    }

    time(label) {
        if (!this.enabled) return;
        console.time(`[TIMER] ${label}`);
    }

    timeEnd(label) {
        if (!this.enabled) return;
        console.timeEnd(`[TIMER] ${label}`);
    }

    showDebugIndicator() {
        let indicator = document.getElementById('debugIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'debugIndicator';
            indicator.className = 'debug-indicator';
            indicator.innerHTML = `
                <span class="debug-icon">🐛</span>
                <span class="debug-label">DEBUG MODE</span>
                <button class="debug-toggle" onclick="window.debug.disable()">×</button>
            `;
            document.body.appendChild(indicator);
        }
        indicator.style.display = 'flex';
    }

    hideDebugIndicator() {
        const indicator = document.getElementById('debugIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    // Network request logging
    logRequest(method, url, data = null) {
        if (!this.enabled) return;
        
        this.group(`${method} ${url}`, () => {
            console.log('Method:', method);
            console.log('URL:', url);
            if (data) {
                console.log('Data:', data);
            }
            console.log('Time:', new Date().toISOString());
        });
    }

    logResponse(url, status, data = null) {
        if (!this.enabled) return;
        
        const statusColor = status < 300 ? '#39ff14' : status < 500 ? '#ffa07a' : '#e94560';
        console.log(
            `%c[RESPONSE] ${url} - Status: ${status}`,
            `color: ${statusColor}; font-weight: bold;`,
            data || ''
        );
    }

    // DOM inspection
    inspectElement(selector) {
        if (!this.enabled) return;
        
        const element = document.querySelector(selector);
        this.group(`Element: ${selector}`, () => {
            console.log('Element:', element);
            console.log('Computed Style:', element ? window.getComputedStyle(element) : null);
            console.log('Event Listeners:', element ? getEventListeners(element) : null);
        });
    }

    // Performance monitoring
    markPerformance(label) {
        if (!this.enabled) return;
        performance.mark(label);
        this.log(`Performance mark: ${label}`);
    }

    measurePerformance(name, startMark, endMark) {
        if (!this.enabled) return;
        performance.measure(name, startMark, endMark);
        const measure = performance.getEntriesByName(name)[0];
        this.info(`Performance: ${name}`, { duration: `${measure.duration.toFixed(2)}ms` });
    }
}

// Initialize global debug instance
window.debug = new Debug();

// Add console command to toggle debug mode
window.enableDebug = () => window.debug.enable();
window.disableDebug = () => window.debug.disable();
window.toggleDebug = () => window.debug.toggle();

// Log initialization
window.debug.log('Retro Cassette Music - Debug utilities loaded');
window.debug.info('Use enableDebug() or add ?debug=true to URL to enable debug mode');
