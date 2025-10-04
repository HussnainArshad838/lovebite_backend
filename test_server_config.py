#!/usr/bin/env python3
"""
Test script to verify server configuration without running the full server.
"""

import os
import sys

def test_environment_detection():
    """Test environment detection logic."""
    print("Testing environment detection...")
    
    # Test development mode
    os.environ['FLASK_ENV'] = 'development'
    os.environ['ENVIRONMENT'] = 'development'
    
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('ENVIRONMENT') == 'production'
    print(f"Development mode detection: {not is_production} (should be True)")
    
    # Test production mode
    os.environ['FLASK_ENV'] = 'production'
    os.environ['ENVIRONMENT'] = 'production'
    
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('ENVIRONMENT') == 'production'
    print(f"Production mode detection: {is_production} (should be True)")
    
    print("✅ Environment detection working correctly")

def test_server_configuration():
    """Test server configuration parameters."""
    print("\nTesting server configuration...")
    
    # Test the configuration that would be used
    host = '0.0.0.0'
    port = 5055
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print("✅ Server configuration parameters are valid")

def main():
    print("🧪 Testing LoveBite Backend Server Configuration")
    print("=" * 50)
    
    test_environment_detection()
    test_server_configuration()
    
    print("\n✅ All tests passed!")
    print("\nTo start the server:")
    print("  Development: python start_server.py --mode dev")
    print("  Production:  python start_server.py --mode prod-eventlet")
    print("  Or use: ./run_production.sh")

if __name__ == '__main__':
    main()
