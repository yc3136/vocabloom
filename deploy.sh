#!/bin/bash

# Vocabloom Full Stack Deployment Script
# This script builds and deploys both frontend and backend

set -e  # Exit on any error

echo "🚀 Starting Vocabloom Full Stack Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -d "client" ] && [ ! -d "server" ]; then
    print_error "Please run this script from the vocabloom root directory"
    exit 1
fi

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed"
        exit 1
    fi
    
    if ! command -v firebase &> /dev/null; then
        print_error "Firebase CLI is not installed"
        exit 1
    fi
    
    print_success "All dependencies are installed"
}

# Deploy backend
deploy_backend() {
    print_status "Deploying backend to Cloud Run..."
    
    cd server
    
    # Check if Dockerfile exists
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found in server directory"
        exit 1
    fi
    
    # Deploy to Cloud Run
    print_status "Building and deploying backend..."
    gcloud run deploy vocabloom-api \
        --source . \
        --region=us-central1 \
        --allow-unauthenticated \
        --platform=managed \
        --quiet
    
    print_success "Backend deployed successfully!"
    cd ..
}

# Deploy frontend
deploy_frontend() {
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
    firebase deploy --only hosting --quiet
    
    print_success "Frontend deployed successfully!"
    cd ..
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Get the backend URL
    BACKEND_URL=$(gcloud run services describe vocabloom-api --region=us-central1 --format="value(status.url)")
    
    print_status "Testing backend health endpoint..."
    if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
        print_success "Backend health check passed"
    else
        print_warning "Backend health check failed"
    fi
    
    print_status "Testing backend root endpoint..."
    if curl -f "$BACKEND_URL/" > /dev/null 2>&1; then
        print_success "Backend root endpoint working"
    else
        print_warning "Backend root endpoint failed"
    fi
    
    print_success "Deployment testing completed"
}

# Main deployment process
main() {
    print_status "Starting Vocabloom deployment..."
    
    # Check dependencies
    check_dependencies
    
    # Deploy backend first
    deploy_backend
    
    # Deploy frontend
    deploy_frontend
    
    # Test deployment
    test_deployment
    
    print_success "🎉 Vocabloom Full Stack Deployment Complete!"
    print_status "Your application is now live!"
    print_status "🌐 Custom Domain: https://vocabloom.app"
    print_status "🔗 API Endpoint: https://api.vocabloom.app"
    print_status "📊 Firebase Console: https://console.firebase.google.com/project/[PROJECT-ID]/hosting"
    print_status "☁️  Cloud Run Console: https://console.cloud.google.com/run/detail/[REGION]/[SERVICE-NAME]"
}

# Run the main function
main "$@" 