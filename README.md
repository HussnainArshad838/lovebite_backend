# LoveBite APK Tracking System

A comprehensive system to track APK installations worldwide for the LoveBite app.

## Features

- 🌍 **Global Installation Tracking**: Track APK installations from anywhere in the world
- 📊 **Real-time Dashboard**: Beautiful admin dashboard to view installation statistics
- 📱 **Device Information**: Collect detailed device information including location, model, OS version
- 💓 **Heartbeat System**: Track active devices with periodic heartbeat signals
- 📈 **Analytics**: View installation statistics by country, version, and time
- 🔍 **Device Lookup**: Find specific devices by device ID

## Quick Start

### 1. Start the Backend Server

```bash
cd lovebite_backend
python3 start_server.py
```

The server will start on port 5055 and you can access:
- **API**: http://localhost:5055
- **Admin Dashboard**: http://localhost:5055/admin_dashboard.html

### 2. Update React Native App

The React Native app has been modified to automatically track installations. When users install and open the app, it will:

1. Detect if it's a new installation
2. Collect device information (brand, model, location, etc.)
3. Send installation data to the backend
4. Send periodic heartbeat signals to track active devices

### 3. View Installation Data

Open the admin dashboard at `http://localhost:5055/admin_dashboard.html` to see:
- Total installations
- Active devices
- Installations by country
- Device details
- Real-time statistics

## API Endpoints

### Track Installation
```
POST /api/track-installation
Content-Type: application/json

{
  "device_id": "unique_device_id",
  "app_version": "1.0.0",
  "device_info": {
    "brand": "Samsung",
    "model": "Galaxy S21",
    "country": "Pakistan",
    "city": "Karachi",
    // ... more device info
  }
}
```

### Get Installations
```
GET /api/installations?page=1&limit=50&country=Pakistan&active_only=true
```

### Get Statistics
```
GET /api/stats
```

### Device Heartbeat
```
POST /api/device/{device_id}/heartbeat
```

## Database Schema

The system uses MongoDB with the following collections:

### apk_installations
```json
{
  "_id": "ObjectId",
  "device_id": "unique_device_id",
  "app_version": "1.0.0",
  "device_info": {
    "brand": "Samsung",
    "model": "Galaxy S21",
    "systemName": "Android",
    "systemVersion": "12",
    "country": "Pakistan",
    "city": "Karachi",
    "timezone": "Asia/Karachi",
    // ... more device details
  },
  "installation_time": "2024-01-01T00:00:00Z",
  "last_seen": "2024-01-01T00:00:00Z",
  "ip_address": "192.168.1.1",
  "is_active": true
}
```

## Configuration

### Backend Configuration
- **Port**: 5055 (configurable in app.py)
- **MongoDB**: Uses the provided MongoDB Atlas connection
- **Database**: lovebite
- **Collection**: apk_installations

### React Native Configuration
- **API URL**: Update `API_BASE_URL` in `InstallationTracker.ts`
- **Heartbeat Interval**: 5 minutes (configurable)
- **Auto-tracking**: Enabled by default

## Security Considerations

1. **API Security**: Consider adding authentication for production use
2. **Data Privacy**: Ensure compliance with privacy laws (GDPR, etc.)
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Data Encryption**: Consider encrypting sensitive device information

## Monitoring

The system provides several monitoring features:

1. **Real-time Dashboard**: View live installation data
2. **Device Status**: Track active vs inactive devices
3. **Geographic Distribution**: See where your app is being used
4. **Version Analytics**: Track app version adoption

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Check MongoDB URI in app.py
   - Ensure MongoDB Atlas cluster is accessible

2. **API Not Responding**
   - Check if server is running on port 5055
   - Verify firewall settings

3. **React Native Tracking Not Working**
   - Check API_BASE_URL in InstallationTracker.ts
   - Ensure device has internet connection
   - Check console logs for errors

### Logs

- **Backend Logs**: Check terminal output where server is running
- **React Native Logs**: Use `npx react-native log-android` or `npx react-native log-ios`

## Production Deployment

For production deployment:

1. **Update API URLs**: Change localhost to your production server
2. **Add Authentication**: Implement API authentication
3. **Use HTTPS**: Ensure all communications are encrypted
4. **Database Security**: Use proper MongoDB security settings
5. **Monitoring**: Set up proper logging and monitoring

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Ensure MongoDB connection is working
4. Check network connectivity

---

**Note**: This system is designed for tracking legitimate app installations. Ensure you comply with all applicable privacy laws and regulations in your jurisdiction.
