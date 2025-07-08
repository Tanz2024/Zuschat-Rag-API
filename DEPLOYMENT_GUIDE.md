# 🚀 ZUS Coffee AI Assistant - Complete Deployment Guide

## 📋 **Overview**

This comprehensive guide covers deployment strategies for the ZUS Coffee AI Assistant across different platforms including Vercel (frontend), Render (backend), and self-hosted options.

---

## 🏗️ **Architecture Overview**

```mermaid
graph TB
    subgraph "Production Architecture"
        A[Users] --> B[Cloudflare CDN]
        B --> C[Vercel Frontend]
        C --> D[API Gateway]
        D --> E[Render Backend]
        E --> F[PostgreSQL DB]
        E --> G[Vector Store]
        E --> H[File Storage]
    end
    
    subgraph "Monitoring"
        I[Error Tracking]
        J[Performance Monitoring]
        K[Log Aggregation]
    end
    
    E --> I
    E --> J
    E --> K
```

---

## 🌐 **Frontend Deployment (Vercel)**

### **Prerequisites**

- GitHub repository with frontend code
- Vercel account
- Domain name (optional)

### **Step 1: Prepare Frontend**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Test production build locally
npm start
```

### **Step 2: Vercel Configuration**

Create `vercel.json` in the frontend directory:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["sin1", "hkg1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url",
    "NEXT_PUBLIC_APP_ENV": "@app_env"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "@api_url"
    }
  },
  "functions": {
    "pages/api/**/*.js": {
      "maxDuration": 30
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-backend-domain.onrender.com/$1",
      "permanent": false
    }
  ]
}
```

### **Step 3: Deploy to Vercel**

#### **Option A: Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd frontend
vercel

# Deploy to production
vercel --prod
```

#### **Option B: GitHub Integration**

1. **Connect Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Build Settings**
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

3. **Environment Variables**
   ```
   NEXT_PUBLIC_API_URL = https://your-backend.onrender.com
   NEXT_PUBLIC_APP_ENV = production
   NEXT_PUBLIC_ANALYTICS_ID = your-analytics-id
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically deploy on every push to main branch

### **Step 4: Custom Domain (Optional)**

```bash
# Add custom domain
vercel domains add yourdomain.com

# Configure DNS
# Add CNAME record: www -> cname.vercel-dns.com
# Add A record: @ -> 76.76.19.19
```

### **Vercel Deployment Checklist**

- [ ] Build succeeds locally
- [ ] Environment variables set
- [ ] API routes working
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] CDN caching optimized
- [ ] Performance metrics green

---

## 🔧 **Backend Deployment (Render)**

### **Prerequisites**

- GitHub repository with backend code
- Render account
- PostgreSQL database (optional)

### **Step 1: Prepare Backend**

```bash
# Navigate to backend directory
cd backend

# Test locally
python -m pytest tests/
uvicorn main:app --reload

# Freeze dependencies
pip freeze > requirements.txt
```

### **Step 2: Render Configuration**

Create `render.yaml` in the project root:

```yaml
services:
  - type: web
    name: zus-coffee-api
    env: python
    plan: starter
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: FASTAPI_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: zus-coffee-db
          property: connectionString
      - key: CORS_ORIGINS
        value: https://your-frontend-domain.vercel.app
      - key: LOG_LEVEL
        value: INFO
    autoDeploy: true
    branch: main
    rootDir: .
    disk:
      name: zus-coffee-disk
      mountPath: /data
      sizeGB: 10

databases:
  - name: zus-coffee-db
    databaseName: zuscoffee
    user: zuscoffee_user
    plan: starter
    region: singapore
    
static:
  - type: static
    name: zus-coffee-assets
    staticPublishPath: ./backend/static
    buildCommand: echo "Static assets ready"
    pullRequestPreviewsEnabled: true
```

### **Step 3: Environment Variables**

Create `.env.production` in backend directory:

```env
# Application Configuration
FASTAPI_ENV=production
API_HOST=0.0.0.0
API_PORT=$PORT
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/dbname

# AI Model Configuration
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
MODEL_CACHE_DIR=/tmp/models

# CORS Configuration
CORS_ORIGINS=["https://your-frontend.vercel.app", "https://www.yourdomain.com"]

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
REDIS_URL=redis://localhost:6379/0
S3_BUCKET_NAME=zus-coffee-assets
S3_REGION=ap-southeast-1

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
NEW_RELIC_LICENSE_KEY=your-newrelic-key
```

### **Step 4: Deploy to Render**

#### **Option A: Render Dashboard**

1. **Create Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repository

2. **Configure Service**
   ```
   Name: zus-coffee-api
   Environment: Python 3
   Region: Singapore
   Branch: main
   Root Directory: (leave empty)
   Build Command: cd backend && pip install -r requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Set Environment Variables**
   - Copy variables from `.env.production`
   - Set `DATABASE_URL` from database connection string

4. **Deploy**
   - Click "Create Web Service"
   - Monitor deployment logs

#### **Option B: Infrastructure as Code**

```bash
# Install Render CLI
curl -fsSL https://cli.render.com/install | sh

# Login
render auth login

# Deploy with configuration file
render deploy --config render.yaml
```

### **Database Setup**

#### **PostgreSQL on Render**

1. **Create Database**
   ```
   Name: zus-coffee-db
   Database: zuscoffee
   User: zuscoffee_user
   Region: Singapore
   Plan: Starter ($7/month)
   ```

2. **Initialize Schema**
   ```sql
   -- Create tables
   CREATE TABLE outlets (
     id SERIAL PRIMARY KEY,
     name VARCHAR(255) NOT NULL,
     address TEXT NOT NULL,
     city VARCHAR(100) NOT NULL,
     state VARCHAR(100) NOT NULL,
     latitude DECIMAL(10, 8),
     longitude DECIMAL(11, 8),
     phone VARCHAR(20),
     operating_hours JSONB,
     services TEXT[],
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- Create indexes
   CREATE INDEX idx_outlets_location ON outlets (latitude, longitude);
   CREATE INDEX idx_outlets_city ON outlets (city);
   
   -- Insert sample data
   INSERT INTO outlets (name, address, city, state, latitude, longitude, phone, operating_hours, services)
   VALUES 
   ('ZUS Coffee KLCC', 'Suria KLCC, Level G, Kuala Lumpur', 'Kuala Lumpur', 'Selangor', 3.1578, 101.7119, '+603-2166-8888', 
    '{"monday": "8:00 AM - 10:00 PM", "tuesday": "8:00 AM - 10:00 PM"}', 
    ARRAY['wifi', 'parking', 'outdoor_seating']);
   ```

### **Render Deployment Checklist**

- [ ] Dependencies installed successfully
- [ ] Environment variables configured
- [ ] Database connected
- [ ] Health check endpoint responding
- [ ] SSL certificate active
- [ ] Custom domain configured (optional)
- [ ] Monitoring alerts set up

---

## 🐳 **Docker Deployment**

### **Backend Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Frontend Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production image
FROM node:18-alpine AS runner

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### **Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/zuscoffee
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped
    volumes:
      - ./backend/data:/app/data

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=zuscoffee
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

### **Deploy with Docker**

```bash
# Build and run
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3

# View logs
docker-compose logs -f

# Update services
docker-compose pull
docker-compose up -d
```

---

## ☁️ **Cloud Provider Deployments**

### **AWS Deployment**

#### **Using AWS Elastic Beanstalk**

```yaml
# .ebextensions/01_packages.config
packages:
  yum:
    git: []
    postgresql15-devel: []

# .ebextensions/02_python.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
```

#### **Using AWS ECS**

```json
{
  "family": "zus-coffee-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "zus-coffee-api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/zus-coffee-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/zus-coffee-api",
          "awslogs-region": "ap-southeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### **Google Cloud Platform**

#### **App Engine Deployment**

```yaml
# app.yaml
runtime: python39

env_variables:
  DATABASE_URL: postgresql://...
  CORS_ORIGINS: https://your-domain.com

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

resources:
  cpu: 1
  memory_gb: 0.5
  disk_size_gb: 10

handlers:
  - url: /.*
    script: auto
    secure: always
    redirect_http_response_code: 301
```

### **Azure Deployment**

#### **Azure Container Instances**

```yaml
# azure-container-instance.yaml
apiVersion: 2019-12-01
location: southeastasia
name: zus-coffee-api
properties:
  containers:
  - name: zus-coffee-api
    properties:
      image: your-registry.azurecr.io/zus-coffee-api:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 1
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: DATABASE_URL
        value: postgresql://...
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 8000
  restartPolicy: Always
```

---

## 📊 **Monitoring & Observability**

### **Health Checks**

```python
# backend/health.py
from fastapi import APIRouter
import psutil
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "database": await check_database(),
        "ai_model": await check_ai_model()
    }
```

### **Logging Configuration**

```python
# backend/logging_config.py
import logging
import structlog
from pythonjsonlogger import jsonlogger

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter())
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler]
    )
```

### **Error Tracking with Sentry**

```python
# backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration(auto_enabling=True)],
    traces_sample_rate=0.1,
    environment="production"
)
```

---

## 🔒 **Security Configuration**

### **SSL/TLS Setup**

#### **Nginx Configuration**

```nginx
# nginx.conf
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Environment Security**

```bash
# Use secrets management
export DATABASE_URL=$(kubectl get secret db-secret -o jsonpath='{.data.url}' | base64 -d)
export SECRET_KEY=$(openssl rand -hex 32)

# Rotate secrets regularly
kubectl create secret generic api-secrets \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=secret-key=$SECRET_KEY
```

---

## 🧪 **Testing in Production**

### **Smoke Tests**

```bash
#!/bin/bash
# smoke-test.sh

BASE_URL="https://your-api-domain.com"

echo "Running production smoke tests..."

# Test health endpoint
curl -f "$BASE_URL/health" || exit 1
echo "✅ Health check passed"

# Test chat endpoint
response=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "context": []}')

if echo "$response" | grep -q "response"; then
  echo "✅ Chat endpoint working"
else
  echo "❌ Chat endpoint failed"
  exit 1
fi

# Test product search
curl -f "$BASE_URL/products/search?query=coffee&limit=1" || exit 1
echo "✅ Product search working"

echo "🎉 All smoke tests passed!"
```

### **Load Testing**

```python
# load_test.py
import asyncio
import aiohttp
import time

async def chat_request(session, message):
    async with session.post('/chat', json={'message': message, 'context': []}) as resp:
        return await resp.json()

async def load_test():
    base_url = 'https://your-api-domain.com'
    connector = aiohttp.TCPConnector(limit=100)
    
    async with aiohttp.ClientSession(base_url, connector=connector) as session:
        start_time = time.time()
        
        # Create 100 concurrent requests
        tasks = [chat_request(session, f"Test message {i}") for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Completed 100 requests in {duration:.2f} seconds")
        print(f"Average response time: {duration/100:.3f} seconds")
        print(f"Requests per second: {100/duration:.2f}")

if __name__ == "__main__":
    asyncio.run(load_test())
```

---

## 📈 **Performance Optimization**

### **CDN Configuration**

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/static/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  images: {
    domains: ['your-cdn-domain.com'],
    loader: 'cloudinary',
    path: 'https://your-cdn-domain.com/',
  },
};
```

### **Database Optimization**

```sql
-- PostgreSQL optimization
-- backend/database_optimization.sql

-- Create indexes for common queries
CREATE INDEX CONCURRENTLY idx_outlets_location_gist 
ON outlets USING GIST (ll_to_earth(latitude, longitude));

CREATE INDEX CONCURRENTLY idx_products_name_gin 
ON products USING GIN (to_tsvector('english', name));

-- Analyze tables
ANALYZE outlets;
ANALYZE products;

-- Update statistics
UPDATE pg_stat_user_tables SET n_tup_ins = 0, n_tup_upd = 0, n_tup_del = 0;
```

### **Caching Strategy**

```python
# backend/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis.from_url(os.getenv('REDIS_URL'))

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expiration=600)
async def search_products(query: str):
    # Expensive product search operation
    pass
```

---

## 🚨 **Disaster Recovery**

### **Backup Strategy**

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
pg_dump $DATABASE_URL | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# File backup
tar -czf "$BACKUP_DIR/files_backup_$DATE.tar.gz" /app/data

# Upload to S3
aws s3 cp "$BACKUP_DIR/" s3://your-backup-bucket/ --recursive

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### **Recovery Procedures**

```bash
#!/bin/bash
# restore.sh

BACKUP_DATE=$1

if [ -z "$BACKUP_DATE" ]; then
  echo "Usage: ./restore.sh YYYYMMDD_HHMMSS"
  exit 1
fi

# Download from S3
aws s3 cp "s3://your-backup-bucket/db_backup_$BACKUP_DATE.sql.gz" ./

# Restore database
gunzip "db_backup_$BACKUP_DATE.sql.gz"
psql $DATABASE_URL < "db_backup_$BACKUP_DATE.sql"

echo "Database restored from backup: $BACKUP_DATE"
```

---

## 📊 **Deployment Checklist**

### **Pre-Deployment**

- [ ] Code reviewed and tested
- [ ] Security vulnerabilities scanned
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] SSL certificates valid
- [ ] Database migrations ready
- [ ] Monitoring configured

### **Deployment**

- [ ] Deploy to staging environment
- [ ] Run smoke tests
- [ ] Verify functionality
- [ ] Deploy to production
- [ ] Monitor deployment metrics
- [ ] Verify health checks
- [ ] Test critical user journeys

### **Post-Deployment**

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify logs are flowing
- [ ] Test backup procedures
- [ ] Update status page
- [ ] Notify stakeholders

---

## 🎯 **Best Practices**

### **Deployment Principles**

1. **Zero Downtime**: Use blue-green or rolling deployments
2. **Rollback Ready**: Always have a rollback plan
3. **Monitor Everything**: Comprehensive observability
4. **Automate Testing**: Continuous integration/deployment
5. **Security First**: Regular security audits
6. **Document Process**: Keep deployment docs updated

### **Common Pitfalls to Avoid**

- ❌ Hardcoded secrets in code
- ❌ Missing health checks
- ❌ No monitoring/alerting
- ❌ Insufficient testing
- ❌ No backup strategy
- ❌ Poor error handling
- ❌ Missing SSL/security headers

---

## 📞 **Support & Troubleshooting**

### **Common Issues**

#### **Build Failures**

```bash
# Clear caches
npm run clean
rm -rf node_modules .next
npm install

# Check Node/Python versions
node --version
python --version
```

#### **Database Connection Issues**

```python
# Test database connection
import psycopg2
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### **CORS Issues**

```python
# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Getting Help**

- **GitHub Issues**: [Project Issues](https://github.com/Tanz2024/Zuschat-Rag-API/issues)
- **Documentation**: Check this guide and API docs
- **Community**: Stack Overflow with `zus-coffee-api` tag

---

**Deployment Guide Version**: 1.0.0  
**Last Updated**: July 9, 2025  
**Next Review**: August 9, 2025

*This guide is continuously updated. Please check for the latest version before deployment.*
