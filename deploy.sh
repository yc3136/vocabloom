#!/bin/bash

# Vocabloom Unified Deployment Script
# Usage: ./deploy.sh [OPTIONS]
# Options:
#   --database, -d     Setup database (in addition to regular deployment)
#   --help, -h         Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Show help
show_help() {
    echo "Vocabloom Unified Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --database, -d     Setup database (in addition to regular deployment)"
    echo "  --help, -h         Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh              # Deploy backend + frontend"
    echo "  ./deploy.sh --database   # Deploy backend + frontend + setup database"
    echo ""
}

# Parse command line arguments
SETUP_DATABASE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --database|-d)
            SETUP_DATABASE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

echo "🚀 Vocabloom Deployment Script"
echo "Targets:"
echo "  ✅ Backend deployment"
echo "  ✅ Frontend deployment"
echo "  ✅ Redis setup"
[ "$SETUP_DATABASE" = true ] && echo "  ✅ Database setup"
echo ""

# Check if we're in the right directory
if [ ! -d "client" ] || [ ! -d "server" ]; then
    print_error "Please run this script from the vocabloom root directory"
    exit 1
fi

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Always check for deployment dependencies
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
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed"
        exit 1
    fi
    
    print_success "All required dependencies are installed"
}

# Setup production Redis
setup_production_redis() {
    print_status "Setting up production Redis (Memorystore)..."
    
    # Check if Redis instance already exists
    if gcloud redis instances describe vocabloom-redis --region=us-central1 --quiet 2>/dev/null; then
        print_status "Redis instance already exists"
    else
        # Create Redis instance
        print_status "Creating Redis instance..."
        gcloud redis instances create vocabloom-redis \
            --size=1 \
            --region=us-central1 \
            --redis-version=redis_6_x \
            --tier=BASIC \
            --quiet
    fi
    
    # Get Redis connection info
    REDIS_HOST=$(gcloud redis instances describe vocabloom-redis --region=us-central1 --format="value(host)")
    REDIS_PORT=$(gcloud redis instances describe vocabloom-redis --region=us-central1 --format="value(port)")
    
    print_success "Redis setup completed!"
    print_status "Redis Host: $REDIS_HOST:$REDIS_PORT"
}

# Setup production database
setup_production_database() {
    print_status "Setting up production database..."
    
    # Create database if it doesn't exist
    print_status "Creating vocabloom database..."
    gcloud sql databases create vocabloom --instance=vocabloom-db --quiet 2>/dev/null || echo "Database vocabloom already exists"
    
    # Get the password from Secret Manager
    print_status "Getting database password from Secret Manager..."
    DB_PASSWORD=$(gcloud secrets versions access latest --secret="database-password")
    
    if [ -z "$DB_PASSWORD" ]; then
        print_error "Could not retrieve database password from Secret Manager"
        exit 1
    fi
    
    # Create user if it doesn't exist, or update password if it does
    print_status "Creating/updating database user..."
    gcloud sql users create vocabloom-app --instance=vocabloom-db --password="$DB_PASSWORD" --quiet 2>/dev/null || \
    gcloud sql users set-password vocabloom-app --instance=vocabloom-db --password="$DB_PASSWORD" --quiet
    
    # Get the database connection info
    DB_HOST=$(gcloud sql instances describe vocabloom-db --format="value(connectionName)")
    PROD_DATABASE_URL="postgresql://vocabloom-app:$DB_PASSWORD@/$DB_HOST/vocabloom"
    
    print_success "Database setup completed!"
    print_status "Database URL: $PROD_DATABASE_URL"
}

# Run production database migrations
run_production_migrations() {
    print_status "Running production database migrations..."
    
    if [ -f "migrate_production_db.sh" ]; then
        ./migrate_production_db.sh
        print_success "Database migrations completed!"
    else
        print_warning "Migration script not found, skipping migration"
        print_status "Database schema will be updated when application starts"
    fi
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
    
    # Get Redis connection info
    REDIS_HOST=$(gcloud redis instances describe vocabloom-redis --region=us-central1 --format="value(host)")
    REDIS_PORT=$(gcloud redis instances describe vocabloom-redis --region=us-central1 --format="value(port)")
    
    # Deploy to Cloud Run with Cloud SQL Auth Proxy
    print_status "Building and deploying backend..."
    gcloud run deploy vocabloom-api \
        --source . \
        --region=us-central1 \
        --allow-unauthenticated \
        --platform=managed \
        --add-cloudsql-instances=vocabloom-467020:us-central1:vocabloom-db \
        --set-env-vars="GOOGLE_CLOUD_PROJECT=vocabloom-467020,ENVIRONMENT=production,DB_USER=vocabloom-app,DB_NAME=vocabloom,DB_HOST=/cloudsql/vocabloom-467020:us-central1:vocabloom-db,REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT" \
        --set-secrets="DB_PASSWORD=database-password:latest,GEMINI_API_KEY=gemini-api-key:latest" \
        --quiet
    
    print_success "Backend deployed successfully!"
    cd ..
}

# Deploy frontend
deploy_frontend() {
    print_status "Deploying frontend to Firebase Hosting..."
    
    # Get the current backend URL dynamically
    print_status "Getting current backend URL..."
    BACKEND_URL=$(gcloud run services describe vocabloom-api --region=us-central1 --format="value(status.url)")
    
    if [ -z "$BACKEND_URL" ]; then
        print_error "Could not get backend URL. Make sure the backend is deployed first."
        exit 1
    fi
    
    print_status "Backend URL: $BACKEND_URL"
    
    cd client
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm install
    
    # Create production .env file with dynamic backend URL
    print_status "Creating production environment file..."
    if [ -f ".env" ]; then
        source .env
        cat > .env.production << EOF
# API Configuration
VITE_API_BASE_URL=$BACKEND_URL

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
VITE_API_BASE_URL=$BACKEND_URL

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
    
    # Setup database if requested
    if [ "$SETUP_DATABASE" = true ]; then
        setup_production_database
        run_production_migrations
    fi
    
    # Always setup Redis and deploy backend and frontend
    setup_production_redis
    deploy_backend
    deploy_frontend
    
    # Test deployment
    test_deployment
    
    # Show final status
    print_success "🎉 Vocabloom Deployment Complete!"
    
    print_status "🌐 Frontend: https://vocabloom.app"
    BACKEND_URL=$(gcloud run services describe vocabloom-api --region=us-central1 --format="value(status.url)")
    print_status "🔗 Backend: $BACKEND_URL"
    print_status "📚 API Docs: $BACKEND_URL/docs"
    
    if [ "$SETUP_DATABASE" = true ]; then
        print_status "🗄️  Database: Cloud SQL PostgreSQL (vocabloom-db)"
        print_status "🔐 Schema: Auto-migrated during deployment"
    fi
    
    print_status "📊 Firebase Console: https://console.firebase.google.com/project/vocabloom-467020/hosting"
    print_status "☁️  Cloud Run Console: https://console.cloud.google.com/run/detail/us-central1/vocabloom-api"
    print_status "🔴 Redis Console: https://console.cloud.google.com/memorystore/redis/instances"
}

# Run the main function
main "$@" 