# Render PostgreSQL Deployment Guide

This guide walks you through deploying your ZUS Coffee chatbot with PostgreSQL on Render.

## Prerequisites

- Render account (free tier available)
- Your code pushed to a Git repository (GitHub recommended)
- PostgreSQL database ready for migration

## Step 1: Create PostgreSQL Database on Render

### 1.1 Log into Render Dashboard
1. Go to [render.com](https://render.com) and sign in
2. Click "New +" and select "PostgreSQL"

### 1.2 Configure Database
```
Name: zuschat-db
Database: zuschat_db
User: zuschat_user
Region: Oregon (US West) or Singapore (closest to your users)
PostgreSQL Version: 15 (recommended)
Plan: Free (for development) or Starter ($7/month for production)
```

### 1.3 Get Connection Details
After creation, you'll get:
- **External Database URL**: `postgresql://zuschat_user:password@dpg-xxxxx-a.oregon-postgres.render.com/zuschat_db`
- **Internal Database URL**: `postgresql://zuschat_user:password@dpg-xxxxx-a:5432/zuschat_db`

## Step 2: Migrate Your Data to Render PostgreSQL

### 2.1 Update Environment Variables
Copy your Render database URL to backend/.env:
```bash
# In backend/.env
DATABASE_URL=postgresql://zuschat_user:your_password@dpg-xxxxx-a.oregon-postgres.render.com/zuschat_db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=60
DB_ECHO=false
```

### 2.2 Run Migration Script
```powershell
# From project root
cd backend
python migrate_to_postgresql.py
```

This will:
- Connect to your Render PostgreSQL database
- Create all tables (outlets, products, conversations, etc.)
- Migrate data from your local SQLite database
- Verify the migration

### 2.3 Verify Migration
```powershell
python check_database.py
```

Expected output:
```
✅ Database connection successful
✅ Found 212 outlets in database
✅ Found 50+ products in database
✅ All tables created successfully
```

## Step 3: Deploy Backend to Render

### 3.1 Create Web Service
1. In Render dashboard, click "New +" → "Web Service"
2. Connect your Git repository
3. Configure the service:

```
Name: zuschat-backend
Environment: Python 3
Region: Same as your database (Oregon recommended)
Branch: main (or your production branch)
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3.2 Set Environment Variables
In the "Environment" tab, add:
```
DATABASE_URL = postgresql://zuschat_user:password@dpg-xxxxx-a.oregon-postgres.render.com/zuschat_db
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 60
DB_ECHO = false
MAX_CONVERSATION_HISTORY = 20
SESSION_TIMEOUT_HOURS = 2
DEBUG = false
LOG_LEVEL = INFO
```

### 3.3 Deploy
Click "Create Web Service" - deployment will start automatically.

## Step 4: Deploy Frontend to Render

### 4.1 Create Static Site
1. Click "New +" → "Static Site"
2. Connect your Git repository
3. Configure:

```
Name: zuschat-frontend
Branch: main
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

### 4.2 Set Environment Variables
In build environment, add:
```
VITE_API_BASE_URL = https://your-backend-url.onrender.com
```

## Step 5: Connect Frontend to Backend

### 5.1 Update Frontend API Configuration
The frontend will automatically use the backend URL from environment variables.

### 5.2 Configure CORS (if needed)
Your backend should already be configured for CORS, but verify in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 6: Verify Deployment

### 6.1 Test Backend
Visit your backend URL: `https://your-backend-url.onrender.com/docs`
You should see the FastAPI documentation.

### 6.2 Test Database Connection
```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "outlets_count": 212
}
```

### 6.3 Test Frontend
Visit your frontend URL and test:
- Chat functionality
- Outlet search ("Find outlets in KL")
- Product search ("Show me coffee menu")
- Dark/light mode toggle

## Step 7: Production Optimization

### 7.1 Database Optimization
- Use Render's Starter plan ($7/month) for better performance
- Enable connection pooling (already configured)
- Monitor database metrics in Render dashboard

### 7.2 Backend Optimization
- Use Render's Starter plan for better CPU/memory
- Enable health checks
- Set up monitoring and alerts

### 7.3 Frontend Optimization
- Configure CDN (Render includes this)
- Enable compression
- Set up custom domain (optional)

## Environment URLs Examples

After deployment, your URLs will look like:
- **Backend**: `https://zuschat-backend.onrender.com`
- **Frontend**: `https://zuschat-frontend.onrender.com`
- **Database**: Internal connection via Render network

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify DATABASE_URL in environment variables
   - Check if database is running in Render dashboard
   - Ensure IP whitelisting (Render handles this automatically)

2. **Backend Deploy Failed**
   - Check build logs in Render dashboard
   - Verify requirements.txt includes all dependencies
   - Ensure start command is correct

3. **Frontend Not Loading**
   - Check if VITE_API_BASE_URL is set correctly
   - Verify build command completed successfully
   - Check browser console for CORS errors

4. **500 Errors in Backend**
   - Check application logs in Render dashboard
   - Verify database connection is working
   - Run health check endpoint

### Getting Help

- Check Render documentation: [render.com/docs](https://render.com/docs)
- Monitor application logs in Render dashboard
- Use the health check endpoints for debugging

## Cost Estimation

**Free Tier (Development)**
- PostgreSQL: Free (expires after 90 days)
- Backend Web Service: Free (750 hours/month)
- Frontend Static Site: Free

**Production (Recommended)**
- PostgreSQL Starter: $7/month
- Backend Starter: $7/month  
- Frontend: Free
- **Total: ~$14/month**

## Security Best Practices

1. **Environment Variables**: Never commit sensitive data to Git
2. **Database Access**: Use the internal URL when possible
3. **CORS**: Restrict to your domain only
4. **HTTPS**: Render provides SSL certificates automatically
5. **API Keys**: Store in Render environment variables, not in code

Your ZUS Coffee chatbot is now ready for production on Render! 🚀
