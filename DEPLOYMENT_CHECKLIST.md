# 🚀 Render Deployment Checklist

Quick checklist to deploy your ZUS Coffee chatbot to Render.

## ✅ Pre-Deployment Checklist

- [ ] Git repository is up to date
- [ ] All test/dummy files removed
- [ ] PostgreSQL migration script ready
- [ ] Environment variables configured
- [ ] Backend runs locally without errors
- [ ] Frontend builds successfully

## 📋 Step-by-Step Deployment

### 1. Create Render PostgreSQL Database (5 minutes)
1. Go to [render.com](https://render.com) → New → PostgreSQL
2. Name: `zuschat-db`
3. Database: `zuschat_db`
4. User: `zuschat_user`
5. Plan: Free (dev) or Starter ($7/month for production)
6. Copy the **External Database URL**

### 2. Migrate Data to Render (2 minutes)
```powershell
# Update backend/.env with your Render database URL
cd backend
python migrate_to_postgresql.py
python check_database.py  # Verify migration
```

### 3. Deploy Backend (10 minutes)
1. Render Dashboard → New → Web Service
2. Connect your Git repo
3. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   ```
   DATABASE_URL = your_render_database_url
   DB_POOL_SIZE = 5
   DEBUG = false
   ```
5. Click "Create Web Service"

### 4. Deploy Frontend (5 minutes)
1. Render Dashboard → New → Static Site
2. Connect your Git repo
3. Settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Environment Variables:
   ```
   VITE_API_BASE_URL = https://your-backend-url.onrender.com
   ```
5. Click "Create Static Site"

### 5. Test Everything (5 minutes)
- [ ] Visit backend URL: `https://your-backend.onrender.com/docs`
- [ ] Test health endpoint: `https://your-backend.onrender.com/health`
- [ ] Visit frontend URL and test chat
- [ ] Test outlet search: "Find KL outlets"
- [ ] Test product search: "Show coffee menu"
- [ ] Toggle dark/light mode

## 🎯 Quick Test Commands

```powershell
# Test backend health
curl https://your-backend.onrender.com/health

# Test outlet search
curl -X POST https://your-backend.onrender.com/chat -H "Content-Type: application/json" -d '{"message": "Find outlets in KL", "session_id": "test123"}'

# Test product search  
curl -X POST https://your-backend.onrender.com/chat -H "Content-Type: application/json" -d '{"message": "Show me coffee menu", "session_id": "test123"}'
```

## 💰 Estimated Costs

| Service | Free Tier | Production |
|---------|-----------|------------|
| PostgreSQL | Free (90 days) | $7/month |
| Backend | 750 hours/month | $7/month |
| Frontend | Unlimited | Free |
| **Total** | **Free** | **$14/month** |

## 🔧 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Database connection failed | Check DATABASE_URL in environment |
| Backend 500 errors | Check logs in Render dashboard |
| Frontend not loading | Verify VITE_API_BASE_URL is correct |
| CORS errors | Check backend CORS configuration |

## 📞 Support Resources

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **PostgreSQL Guide**: [render.com/docs/databases](https://render.com/docs/databases)
- **Project Docs**: See `/docs/` folder in your repository

---

**Total Deployment Time: ~25 minutes**

Your production-ready ZUS Coffee chatbot will be live on Render! 🎉
