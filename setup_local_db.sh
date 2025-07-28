#!/bin/bash

echo "Setting up local PostgreSQL database for Vocabloom..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install it first:"
    echo "  macOS: brew install postgresql"
    echo "  Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Check if PostgreSQL service is running
if ! pg_isready -q; then
    echo "PostgreSQL service is not running. Starting it..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew services start postgresql
    else
        # Linux
        sudo systemctl start postgresql
    fi
fi

# Create database and user
echo "Creating database and user..."

# Create user (if it doesn't exist)
psql -d postgres -c "CREATE USER vocabloom WITH PASSWORD 'vocabloom123';" 2>/dev/null || echo "User vocabloom already exists"

# Create database (if it doesn't exist)
psql -d postgres -c "CREATE DATABASE vocabloom OWNER vocabloom;" 2>/dev/null || echo "Database vocabloom already exists"

# Grant privileges
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE vocabloom TO vocabloom;"

echo "Database setup complete!"
echo "Database URL: postgresql://vocabloom:vocabloom123@localhost:5432/vocabloom"
echo ""
echo "Next steps:"
echo "1. Copy server/env.local to server/.env"
echo "2. Copy client/env.local to client/.env"
echo "3. Update your Gemini API key in server/.env"
echo "4. Restart the backend server" 