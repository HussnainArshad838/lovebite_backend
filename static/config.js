/**
 * Admin Dashboard Configuration
 * Change ENVIRONMENT to switch between local and production
 */

// Environment: 'development' or 'production'
const ENVIRONMENT = 'production';  // Change to 'development' for local testing

// Configuration
const CONFIG = {
    development: {
        API_BASE: 'http://localhost:5055/api',
        WS_BASE: 'http://localhost:5055',
        DEBUG: true
    },
    production: {
        API_BASE: 'https://lovebite-backend-1.onrender.com/api',
        WS_BASE: 'https://lovebite-backend-1.onrender.com',
        DEBUG: false
    }
};

// Export current configuration
const CURRENT_CONFIG = CONFIG[ENVIRONMENT];

// Export for use in admin dashboard
const API_BASE = CURRENT_CONFIG.API_BASE;
const WS_BASE = CURRENT_CONFIG.WS_BASE;
const DEBUG = CURRENT_CONFIG.DEBUG;

// Log configuration
if (DEBUG) {
    console.log('='.repeat(50));
    console.log('🚀 Admin Dashboard Configuration');
    console.log('='.repeat(50));
    console.log('Environment:', ENVIRONMENT.toUpperCase());
    console.log('API Base:', API_BASE);
    console.log('WebSocket Base:', WS_BASE);
    console.log('Debug Mode:', DEBUG);
    console.log('='.repeat(50));
}

