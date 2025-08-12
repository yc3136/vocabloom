#!/bin/bash

# Vocabloom Local Development Stack
# This script sets up and runs the complete local development environment

set -e

echo "🌱 Starting Vocabloom Local Development Stack..."

# Function to check if PostgreSQL is installed and running
check_postgresql() {
    if ! command -v psql &> /dev/null; then
        echo "❌ PostgreSQL is not installed. Installing..."
        brew install postgresql@14
        brew services start postgresql@14
        echo "✅ PostgreSQL installed and started"
    elif ! pg_isready -q; then
        echo "🔄 Starting PostgreSQL service..."
        brew services start postgresql@14
        sleep 2
    else
        echo "✅ PostgreSQL is already running"
    fi
}

# Function to setup local database
setup_database() {
    echo "🗄️  Setting up local database..."
    
    # Create user and database if they don't exist
    psql -d postgres -c "CREATE USER vocabloom WITH PASSWORD 'vocabloom123';" 2>/dev/null || echo "User vocabloom already exists"
    psql -d postgres -c "CREATE DATABASE vocabloom OWNER vocabloom;" 2>/dev/null || echo "Database vocabloom already exists"
    psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE vocabloom TO vocabloom;" 2>/dev/null || echo "Privileges already granted"
    
    echo "✅ Database setup complete"
}

# Function to setup environment files
setup_environment() {
    echo "⚙️  Setting up environment files..."
    
    # Backend environment
    if [ ! -f "server/.env" ]; then
        echo "Creating server/.env with local settings..."
        cat > server/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://vocabloom:vocabloom123@localhost:5432/vocabloom

# Firebase Configuration
FIREBASE_PROJECT_ID=vocabloom-467020

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=local

# Google Cloud Storage Configuration
GCS_BUCKET_NAME=vocabloom-images-local

# Environment
ENVIRONMENT=local
EOF
        echo "✅ Created server/.env with placeholders"
        echo "⚠️  Please update server/.env with your real API keys"
    else
        echo "✅ server/.env already exists"
    fi
    
    # Frontend environment
    if [ ! -f "client/.env" ]; then
        echo "Creating client/.env with local settings..."
        cat > client/.env << EOF
# API Configuration
VITE_API_BASE_URL=http://127.0.0.1:8000

# Firebase Configuration
VITE_FIREBASE_API_KEY=your_firebase_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=vocabloom-467020.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=vocabloom-467020
VITE_FIREBASE_STORAGE_BUCKET=vocabloom-467020.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
VITE_FIREBASE_APP_ID=your_app_id_here

# Environment
VITE_ENVIRONMENT=local
EOF
        echo "✅ Created client/.env with placeholders"
        echo "⚠️  Please update client/.env with your real Firebase keys"
    else
        echo "✅ client/.env already exists"
    fi
    
    echo "✅ Environment files ready"
}

# Function to run database migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    cd server
    
    # Check if alembic is initialized
    if [ ! -d "alembic" ]; then
        echo "Initializing Alembic..."
        poetry run alembic init alembic
        
        # Update alembic.ini
        sed -i '' 's|sqlalchemy.url = driver://user:pass@localhost/dbname|sqlalchemy.url = postgresql://vocabloom:vocabloom123@localhost:5432/vocabloom|' alembic.ini
        sed -i '' 's|version_num_format = %%(version_num)04d|version_num_format = %%(version_num)04d|' alembic.ini
        
        # Update env.py to import our models
        cat > alembic/env.py << 'EOF'
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import Base
from app.models import User, Flashcard, Translation

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF
    fi
    
    # Create and run migration if needed
    if [ ! -f "alembic/versions/initial_migration.py" ]; then
        poetry run alembic revision --autogenerate -m "Initial migration"
    fi
    
    poetry run alembic upgrade head
    cd ..
    echo "✅ Database migrations complete"
}

# Function to setup Google Cloud Storage
setup_gcs() {
    echo "☁️  Setting up Google Cloud Storage..."
    cd server
    
    # Check if GCS bucket setup script exists
    if [ -f "setup_gcs.py" ]; then
        echo "Running GCS bucket setup..."
        poetry run python setup_gcs.py
    else
        echo "⚠️  GCS setup script not found, skipping GCS setup"
    fi
    
    cd ..
    echo "✅ GCS setup complete"
}

# Function to kill existing processes
kill_existing() {
    echo "🛑 Stopping existing processes..."
    
    # Kill processes on specific ports
    for port in 8000 5173 5174; do
        if lsof -ti:$port > /dev/null 2>&1; then
            echo "Killing process on port $port"
            lsof -ti:$port | xargs kill -9
        fi
    done
    
    # Kill any remaining uvicorn or vite processes
    pkill -f "uvicorn\|vite" 2>/dev/null || true
    
    sleep 2
}

# Function to start backend
start_backend() {
    echo "🚀 Starting backend server..."
    cd server
    poetry run python -m uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
            echo "✅ Backend running on http://127.0.0.1:8000 (PID: $BACKEND_PID)"
            break
        fi
        sleep 1
    done
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting frontend server..."
    cd client
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    echo "⏳ Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1 || curl -s http://localhost:5174 > /dev/null 2>&1; then
            echo "✅ Frontend running (PID: $FRONTEND_PID)"
            break
        fi
        sleep 1
    done
}

# Main execution
main() {
    echo "🔧 Setting up local development environment..."
    
    # Check and setup PostgreSQL
    check_postgresql
    
    # Setup database
    setup_database
    
    # Setup environment files
    setup_environment
    
    # Run migrations
    run_migrations
    
    # Setup GCS
    setup_gcs
    
    # Kill existing processes
    kill_existing
    
    # Start backend
    start_backend
    
    # Start frontend
    start_frontend
    
    echo ""
    echo "🎉 Vocabloom Local Stack is running!"
    echo "📱 Frontend: http://localhost:5173 (or http://localhost:5174)"
    echo "🔧 Backend:  http://127.0.0.1:8000"
    echo "📚 API Docs: http://127.0.0.1:8000/docs"
    echo ""
    echo "To stop both servers, run: kill $BACKEND_PID $FRONTEND_PID"
    echo "Or press Ctrl+C to stop this script"
    echo ""
    
    # Wait for user to stop
    wait
}

# Handle script interruption
trap 'echo ""; echo "🛑 Stopping Vocabloom..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0' INT

# Run main function
main 