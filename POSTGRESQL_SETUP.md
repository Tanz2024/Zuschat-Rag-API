# PostgreSQL Setup Guide for ZUS Coffee AI Chatbot

## Quick Setup (Windows)

### 1. Install PostgreSQL

**Option A: Download from Official Site**
1. Go to https://www.postgresql.org/download/windows/
2. Download PostgreSQL installer
3. Run installer and follow setup wizard
4. Remember the password you set for the `postgres` user

**Option B: Using Chocolatey (if installed)**
```powershell
choco install postgresql
```

**Option C: Using Scoop (if installed)**
```powershell
scoop install postgresql
```

### 2. Configure PostgreSQL

1. **Add PostgreSQL to PATH** (if not done automatically):
   - Add `C:\Program Files\PostgreSQL\15\bin` to your system PATH

2. **Verify Installation**:
   ```powershell
   psql --version
   ```

3. **Start PostgreSQL Service** (if not running):
   ```powershell
   # Start service
   net start postgresql-x64-15
   
   # Or use Services.msc GUI
   ```

### 3. Create Database

```powershell
# Connect to PostgreSQL (will prompt for password)
psql -U postgres

# Create database
CREATE DATABASE zuschat;

# Exit
\q
```

### 4. Run Setup Script

```powershell
# Navigate to backend directory
cd backend

# Run setup script
python setup_postgresql.py
```

## Environment Configuration

Update your `.env` file:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/zuschat
```

Replace `YOUR_PASSWORD` with the password you set during PostgreSQL installation.

## Common Issues & Solutions

### Issue: "psql: command not found"
**Solution**: Add PostgreSQL bin directory to PATH
- Default location: `C:\Program Files\PostgreSQL\15\bin`

### Issue: "database does not exist" 
**Solution**: Create the database manually:
```sql
createdb zuschat
```

### Issue: "password authentication failed"
**Solution**: Check your password in the DATABASE_URL

### Issue: "could not connect to server"
**Solution**: Start PostgreSQL service:
```powershell
net start postgresql-x64-15
```

## Manual Migration (if setup script fails)

```powershell
# Run migration script directly
python migrate_to_postgresql.py
```

## Verify Setup

Test the connection:
```powershell
# Test backend
uvicorn main:app --reload

# Test API
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```
