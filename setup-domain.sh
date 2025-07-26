#!/bin/bash

# Vocabloom Custom Domain Setup Script
# This script helps configure DNS records for any custom domain

set -e

echo "🌐 Setting up custom domain for Vocabloom..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

print_instructions() {
    echo -e "${YELLOW}[INSTRUCTIONS]${NC} $1"
}

# Get domain from user input
get_domain() {
    if [ -z "$1" ]; then
        echo -n "Enter your domain (e.g., vocabloom.app): "
        read DOMAIN
    else
        DOMAIN=$1
    fi
    
    # Remove http/https if present
    DOMAIN=$(echo $DOMAIN | sed 's|^https?://||' | sed 's|/.*$||')
    
    echo $DOMAIN
}

# Check if domain is accessible
check_domain() {
    local domain=$1
    print_status "Checking domain availability: $domain"
    
    if nslookup $domain > /dev/null 2>&1; then
        print_success "Domain $domain is accessible"
        return 0
    else
        print_warning "Domain $domain is not yet accessible"
        print_instructions "This is normal for newly registered domains. DNS can take 24-48 hours to propagate."
        return 1
    fi
}

# Get Firebase hosting URL
get_firebase_url() {
    print_status "Getting Firebase hosting URL..."
    
    # This would typically come from Firebase CLI
    # For now, we'll use a placeholder
    FIREBASE_URL="https://[PROJECT-ID].web.app"
    print_success "Firebase URL: $FIREBASE_URL"
    echo $FIREBASE_URL
}

# Get Cloud Run URL
get_backend_url() {
    print_status "Getting Cloud Run URL..."
    
    BACKEND_URL=$(gcloud run services describe vocabloom-api --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "")
    
    if [ -n "$BACKEND_URL" ]; then
        print_success "Backend URL: $BACKEND_URL"
        echo $BACKEND_URL
    else
        print_error "Could not retrieve backend URL. Make sure the service is deployed."
        exit 1
    fi
}

# Display DNS configuration instructions
show_dns_instructions() {
    local domain=$1
    local firebase_url=$2
    local backend_url=$3
    
    print_instructions "Please configure the following DNS records for $domain:"
    echo ""
    echo "=== DNS Records to Add ==="
    echo ""
    echo "1. Frontend (Firebase Hosting):"
    echo "   Type: CNAME"
    echo "   Name: @ (or $domain)"
    echo "   Target: [PROJECT-ID].web.app"
    echo "   Proxy: Yes (Orange Cloud)"
    echo ""
    echo "2. Backend API:"
    echo "   Type: CNAME"
    echo "   Name: api"
    echo "   Target: $(echo $backend_url | sed 's|https://||')"
    echo "   Proxy: Yes (Orange Cloud)"
    echo ""
    echo "3. WWW Redirect:"
    echo "   Type: CNAME"
    echo "   Name: www"
    echo "   Target: [PROJECT-ID].web.app"
    echo "   Proxy: Yes (Orange Cloud)"
    echo ""
    print_instructions "Steps to configure in Cloudflare:"
    echo "1. Go to https://dash.cloudflare.com"
    echo "2. Add your domain: $domain"
    echo "3. Go to DNS > Records"
    echo "4. Add the records above"
    echo "5. Enable the orange cloud (proxy) for all records"
    echo ""
    print_instructions "Steps to configure in Namecheap:"
    echo "1. Go to https://ap.www.namecheap.com/Domains/DomainControlPanel"
    echo "2. Select your domain: $domain"
    echo "3. Go to Advanced DNS"
    echo "4. Add the records above"
    echo "5. Set TTL to Automatic"
    echo ""
}

# Configure Firebase custom domain
configure_firebase_domain() {
    local domain=$1
    print_status "Configuring Firebase custom domain: $domain"
    
    cd client
    
    print_instructions "Adding custom domain to Firebase..."
    firebase hosting:sites:add $domain
    
    print_instructions "Now run: firebase hosting:channel:deploy preview"
    print_instructions "Then: firebase hosting:sites:list"
    
    cd ..
}

# Main setup process
main() {
    # Get domain from command line argument or user input
    DOMAIN=$(get_domain "$1")
    
    print_status "Starting custom domain setup for $DOMAIN..."
    
    # Check if domain is accessible
    if ! check_domain "$DOMAIN"; then
        print_warning "Domain $DOMAIN is not yet accessible"
        print_instructions "This is normal for newly registered domains. You can still configure DNS now."
        print_instructions "The domain will become accessible once DNS propagation is complete (24-48 hours)."
        echo ""
    fi
    
    # Get URLs
    FIREBASE_URL=$(get_firebase_url)
    BACKEND_URL=$(get_backend_url)
    
    # Show DNS instructions
    show_dns_instructions "$DOMAIN" "$FIREBASE_URL" "$BACKEND_URL"
    
    # Configure Firebase
    configure_firebase_domain "$DOMAIN"
    
    print_success "Domain setup instructions completed!"
    print_instructions "After configuring DNS, run: ./deploy.sh"
    print_instructions "Note: DNS propagation can take 24-48 hours for the domain to be fully accessible."
}

# Run the main function
main "$@" 