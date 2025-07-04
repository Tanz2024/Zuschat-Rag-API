# 🚀 RENDER DEPLOYMENT GUIDE - ZUS Coffee Chatbot Backend

## 📋 **Environment Variables for Render**

When deploying to Render, add these **Environment Variables** in your Web Service settings:

### **🔧 Required Environment Variables:**

| Key | Value | Description |
|-----|-------|-------------|
| `DB_POOL_SIZE` | `5` | Database connection pool size |
| `DB_MAX_OVERFLOW` | `10` | Max additional connections |
| `DB_POOL_TIMEOUT` | `60` | Connection timeout in seconds |
| `DB_ECHO` | `false` | SQL query logging (disable in production) |
| `MAX_CONVERSATION_HISTORY` | `20` | Chat history limit |
| `SESSION_TIMEOUT_HOURS` | `2` | Chat session timeout |
| `DEBUG` | `false` | Debug mode (disable in production) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENVIRONMENT` | `production` | Environment identifier |
| `PORT` | `10000` | Application port (Render default) |

### **🗄️ Database Connection:**
- **DATABASE_URL** will be automatically set when you connect your PostgreSQL service
- **Don't manually set DATABASE_URL** unless using external database

---

## 🚀 **Step-by-Step Render Deployment**

### **1. Prepare Your Repository**
```bash
# Make sure you have these files:
✅ backend/main.py (FastAPI app)
✅ backend/requirements.txt (dependencies)
✅ backend/.env (for local development only)
✅ backend/data/ (database models)
✅ Your chatbot code and services
```

### **2. Create Web Service on Render**
1. Go to [render.com](https://render.com)
2. Click **"New"** → **"Web Service"**
3. Connect your **GitHub repository**
4. Select branch: **main**

### **3. Configure Build Settings**
```
Environment: Python 3
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### **4. Add Environment Variables**
In your Web Service → **Environment** tab, add each variable from the table above.

### **5. Connect PostgreSQL Database**
1. In your Web Service → **Environment** tab
2. Click **"Add Database"**
3. Select your existing PostgreSQL service
4. Render will automatically add `DATABASE_URL`

### **6. Deploy**
- Click **"Create Web Service"**
- Render will automatically build and deploy
- Check logs for any issues

---

## 🔍 **Verification Steps**

After deployment, verify your backend is working:

### **1. Health Check**
```
GET https://your-app.onrender.com/health
```
Should return: `{"status": "healthy"}`

### **2. Database Connection**
```
GET https://your-app.onrender.com/vector-store-status
```
Should return database and vector store information.

### **3. Test Chat Endpoint**
```
POST https://your-app.onrender.com/chat
{
  "message": "Hello",
  "session_id": "test123"
}
```

---

## ⚠️ **Important Notes**

### **Environment Variables:**
- Add all variables listed above to Render Environment Variables
- **DATABASE_URL** is auto-generated - don't set manually
- **PORT** should be 10000 (Render's internal port)

### **Database:**
- Your PostgreSQL database should already be running on Render
- Make sure it contains your 243 outlets and 11 products
- Connection will be automatic once linked

### **File Structure:**
```
backend/
├── main.py                    # FastAPI app (✅ Ready)
├── requirements.txt           # Dependencies (✅ Ready)
├── data/
│   ├── database.py           # Database models (✅ Ready)
│   └── products.json         # Product data (✅ Ready)
├── zus_realtime_calculator.py # Real-time calculations (✅ Ready)
├── chatbot_calculator_api.py  # Chatbot API (✅ Ready)
└── [your other services]
```

### **Production Checklist:**
- ✅ Database contains real ZUS Coffee data (243 outlets, 11 products)
- ✅ Real-time calculations implemented
- ✅ No dummy/test data
- ✅ Environment variables configured
- ✅ FastAPI app configured for production
- ✅ Requirements.txt up to date

---

## 🎯 **Your Backend Will Be Available At:**
```
https://your-service-name.onrender.com
```

### **API Endpoints:**
- `POST /chat` - Main chatbot endpoint
- `GET /health` - Health check
- `POST /search-products` - Product search
- `POST /search-outlets` - Outlet search
- `GET /vector-store-status` - System status

---

## 🚀 **Ready to Deploy!**

Your ZUS Coffee chatbot backend is production-ready with:
- ✅ Real outlet and product data
- ✅ Real-time price calculations  
- ✅ PostgreSQL database on Render
- ✅ Proper environment configuration
- ✅ Production-optimized settings

**Just follow the steps above and deploy!** 🎉
