#!/bin/bash

# Vocabloom Frontend Deployment Script

set -e

echo "🚀 Deploying Vocabloom Frontend..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "client" ]; then
    print_error "Please run this script from the vocabloom root directory"
    exit 1
fi

# Check if required tools are installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi

if ! command -v firebase &> /dev/null; then
    print_error "Firebase CLI is not installed"
    exit 1
fi

# Deploy frontend
print_status "Deploying frontend to Firebase Hosting..."

cd client

# Install dependencies
print_status "Installing frontend dependencies..."
npm install

# Set production environment variables
print_status "Setting production environment variables..."
export VITE_API_BASE_URL=https://vocabloom-api-18560061448.us-central1.run.app
export VITE_ENVIRONMENT=production

# Create production .env file for build
print_status "Creating production environment file..."
# Source existing .env file if it exists, otherwise use defaults
if [ -f ".env" ]; then
    source .env
    cat > .env.production << EOF
# API Configuration
VITE_API_BASE_URL=https://vocabloom-api-18560061448.us-central1.run.app

# Firebase Configuration
VITE_FIREBASE_API_KEY=${VITE_FIREBASE_API_KEY:-your_firebase_api_key_here}
VITE_FIREBASE_AUTH_DOMAIN=${VITE_FIREBASE_AUTH_DOMAIN:-vocabloom-467020.firebaseapp.com}
VITE_FIREBASE_PROJECT_ID=${VITE_FIREBASE_PROJECT_ID:-vocabloom-467020}
VITE_FIREBASE_STORAGE_BUCKET=${VITE_FIREBASE_STORAGE_BUCKET:-vocabloom-467020.appspot.com}
VITE_FIREBASE_MESSAGING_SENDER_ID=${VITE_FIREBASE_MESSAGING_SENDER_ID:-your_sender_id_here}
VITE_FIREBASE_APP_ID=${VITE_FIREBASE_APP_ID:-your_app_id_here}

# Environment
VITE_ENVIRONMENT=production
EOF
else
    cat > .env.production << EOF
# API Configuration
VITE_API_BASE_URL=https://vocabloom-api-18560061448.us-central1.run.app

# Firebase Configuration
VITE_FIREBASE_API_KEY=your_firebase_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=vocabloom-467020.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=vocabloom-467020
VITE_FIREBASE_STORAGE_BUCKET=vocabloom-467020.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
VITE_FIREBASE_APP_ID=your_app_id_here

# Environment
VITE_ENVIRONMENT=production
EOF
fi

# Build the app with production environment
print_status "Building frontend with production environment..."
npm run build

# Deploy to Firebase
print_status "Deploying to Firebase Hosting..."
firebase deploy --only hosting

# Clean up production env file
rm -f .env.production

print_success "Frontend deployed successfully!"

cd ..

print_success "🎉 Frontend deployment complete!" 