# Vercel Deployment Checklist ✅

## Pre-Deployment

- [x] Created `api/index.py` entry point
- [x] Swapped requirements files (lightweight version active)
- [x] Updated `vercel.json` configuration
- [x] Added `.vercelignore` file
- [x] Modified `app.py` for Vercel compatibility
- [x] Fixed handler export format

## Before You Deploy

1. **Verify requirements.txt** is the lightweight version:
   ```bash
   cat requirements.txt | grep -i socketio
   ```
   Should return nothing (no SocketIO packages)

2. **Check vercel.json** points to correct entry:
   ```bash
   cat vercel.json | grep "src"
   ```
   Should show `"src": "api/index.py"`

3. **Ensure api/index.py exists:**
   ```bash
   ls api/index.py
   ```

## Deployment Steps

1. **Install Vercel CLI** (if not installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Follow prompts:**
   - Link to existing project or create new
   - Confirm project settings
   - Wait for deployment

## Post-Deployment

1. **Test health endpoint:**
   ```bash
   curl https://your-deployment-url.vercel.app/health
   ```
   Expected: `{"status": "healthy", ...}`

2. **Test main endpoint:**
   ```bash
   curl https://your-deployment-url.vercel.app/
   ```
   Expected: `{"message": "LoveBite APK Tracking API", ...}`

3. **Check Vercel logs:**
   ```bash
   vercel logs
   ```
   Should see: "🔧 Running on Vercel - WebSocket features disabled"

4. **Verify MongoDB connection:**
   Look for: "✅ Connected to MongoDB successfully!"

## Environment Variables (Set in Vercel Dashboard)

Go to your project settings in Vercel dashboard:

- [ ] `MONGODB_URI` - Your MongoDB connection string
- [ ] `FLASK_ENV` - Set to "production"
- [ ] `VERCEL` - Automatically set by Vercel (no action needed)

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'flask_socketio'"
**Solution:** You're using wrong requirements.txt
```bash
mv requirements.txt requirements-full.txt
mv requirements-vercel.txt requirements.txt
vercel --force
```

### Issue: "TypeError: issubclass() arg 1 must be a class"
**Solution:** Already fixed! Using `handler = app` instead of custom function

### Issue: MongoDB connection timeout
**Solution:** Check your MongoDB URI in Vercel environment variables

### Issue: 404 on all endpoints
**Solution:** Verify vercel.json routes configuration

## Success Indicators

✅ Deployment completes without errors
✅ Health endpoint returns 200
✅ MongoDB connects successfully
✅ No Flask-SocketIO errors in logs
✅ Admin dashboard loads
✅ API endpoints respond correctly

## Rollback Plan

If something goes wrong:

1. **Revert to previous deployment:**
   ```bash
   vercel rollback
   ```

2. **Or restore full requirements for Railway:**
   ```bash
   mv requirements.txt requirements-vercel.txt
   mv requirements-full.txt requirements.txt
   git checkout vercel.json
   ```

---

## 🎉 You're Ready!

Everything is configured correctly. Just run:

```bash
vercel
```

And your app will deploy successfully!
