#!/bin/bash
# Render startup script with enhanced error handling and logging

echo "🚀 Starting ZUS Coffee Chatbot Backend..."
echo "Current directory: $(pwd)"
echo "Contents: $(ls -la)"

# Change to backend directory
if [ -d "backend" ]; then
    cd backend
    echo "✅ Changed to backend directory: $(pwd)"
else
    echo "❌ Backend directory not found!"
    exit 1
fi

# Show environment info
echo "📊 Environment Info:"
echo "Python version: $(python --version)"
echo "Port: $PORT"
echo "Database URL: ${DATABASE_URL:0:20}..." # Show first 20 chars only for security

# Test imports before starting server
echo "🔍 Testing critical imports..."
python -c "
import sys
try:
    from main import app
    print('✅ FastAPI app import successful')
    from chatbot.enhanced_minimal_agent import get_chatbot
    print('✅ Chatbot import successful')
    print('🎉 All imports successful - starting server...')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Import test failed - aborting startup"
    exit 1
fi

# Start the server with enhanced logging
echo "🌐 Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info --access-log
