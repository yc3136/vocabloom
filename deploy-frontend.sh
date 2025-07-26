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

# Build the app
print_status "Building frontend..."
npm run build

# Deploy to Firebase
print_status "Deploying to Firebase Hosting..."
firebase deploy --only hosting

print_success "Frontend deployed successfully!"

cd ..

print_success "🎉 Frontend deployment complete!" 