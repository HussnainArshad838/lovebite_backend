#!/usr/bin/env python3
"""
LoveBite APK Tracking Server Startup Script
"""

import subprocess
import sys
import os
import time

def check_virtual_environment():
    """Check if virtual environment exists and activate it"""
    venv_path = os.path.join(os.path.dirname(__file__), "venv")
    if not os.path.exists(venv_path):
        print("📦 Creating virtual environment...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
            print("✅ Virtual environment created!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating virtual environment: {e}")
            return False
    
    # Check if requirements are installed
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "list", "-q"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Virtual environment is ready!")
    except subprocess.CalledProcessError:
        print("📦 Installing required packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing packages: {e}")
            return False
    return True

def start_server():
    """Start the Flask server"""
    print("🚀 Starting LoveBite APK Tracking Server...")
    print("🌐 Server will be available at: http://localhost:5055")
    print("📊 Admin Dashboard: http://localhost:5055/admin_dashboard.html")
    print("📱 API Endpoints:")
    print("   - POST /api/track-installation")
    print("   - GET  /api/installations")
    print("   - GET  /api/stats")
    print("   - GET  /api/device/<device_id>")
    print("   - POST /api/device/<device_id>/heartbeat")
    print("\n" + "="*60)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    print("💕 LoveBite APK Tracking System")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found. Please run this script from the lovebite_backend directory.")
        sys.exit(1)
    
    # Check virtual environment
    if not check_virtual_environment():
        print("❌ Failed to setup virtual environment. Exiting.")
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
