#!/bin/bash

# Hospital Management System - HTTP-only VPS Deployment Script
# Usage: ./deploy-vps.sh [vps-ip]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get VPS IP (optional parameter)
VPS_IP=${1:-"your-vps-ip"}
PROJECT_DIR=$(pwd)

log_info "Starting HTTP-only deployment for VPS IP: $VPS_IP"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please do not run this script as root"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    log_info "Run: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    log_info "Creating .env file from template..."
    cp .env.example .env
    
    # Generate secure passwords
    MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
    MYSQL_PASSWORD=$(openssl rand -base64 32)
    SECRET_KEY=$(openssl rand -base64 64)
    JWT_SECRET_KEY=$(openssl rand -base64 32)
    
    # Update .env file with VPS IP and generated passwords
    sed -i "s/your-domain.com/$VPS_IP/g" .env
    sed -i "s/your_secure_root_password_here/$MYSQL_ROOT_PASSWORD/g" .env
    sed -i "s/your_secure_database_password_here/$MYSQL_PASSWORD/g" .env
    sed -i "s/your_very_secure_secret_key_minimum_32_characters_long/$SECRET_KEY/g" .env
    sed -i "s/your_jwt_secret_key_here/$JWT_SECRET_KEY/g" .env
    
    # Set HTTP API URL for production
    sed -i "s|REACT_APP_API_URL=https://your-domain.com|REACT_APP_API_URL=http://$VPS_IP|g" .env
    
    log_success ".env file created with secure passwords"
    log_warning "Please review and update the .env file with your specific configuration"
else
    log_info ".env file already exists"
fi

# Remove SSL directory since we don't need it
if [ -d "nginx/ssl" ]; then
    log_info "Removing SSL directory (not needed for HTTP-only deployment)"
    rm -rf nginx/ssl
fi

# Stop any existing containers
log_info "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Pull latest images
log_info "Pulling latest base images..."
docker-compose pull || true

# Build and start all services (no profile needed now)
log_info "Building and starting all services..."
docker-compose up --build -d

# Wait for services to be ready
log_info "Waiting for services to start..."
sleep 30

# Check service health
log_info "Checking service health..."
RETRY_COUNT=0
MAX_RETRIES=12

# Check backend health
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker-compose exec backend curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend service is healthy"
        break
    else
        log_info "Waiting for backend service... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
        sleep 10
        RETRY_COUNT=$((RETRY_COUNT + 1))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "Backend service failed to start properly"
    docker-compose logs backend
    exit 1
fi

# Check frontend
if docker-compose exec frontend curl -f http://localhost:3000 > /dev/null 2>&1; then
    log_success "Frontend service is healthy"
else
    log_warning "Frontend service might not be ready yet"
fi

# Check nginx
if docker-compose exec nginx curl -f http://localhost:80/health > /dev/null 2>&1; then
    log_success "Nginx service is healthy"
else
    log_warning "Nginx service might not be ready yet"
fi

# Display service status
log_info "Service status:"
docker-compose ps

# Test external access if VPS_IP is provided and not placeholder
if [ "$VPS_IP" != "your-vps-ip" ]; then
    log_info "Testing external access..."
    if curl -f -s http://$VPS_IP/health > /dev/null; then
        log_success "External access test passed"
    else
        log_warning "External access test failed - check firewall and network settings"
    fi
fi

# Display deployment information
echo
log_success "Deployment completed successfully!"
echo
echo "🌐 Application URLs:"
echo "   Frontend: http://$VPS_IP"
echo "   API:      http://$VPS_IP/api"
echo "   Health:   http://$VPS_IP/health"
echo
echo "🔧 Management Commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Restart services: docker-compose restart"
echo "   Stop services:    docker-compose down"
echo "   Update app:       git pull && docker-compose up --build -d"
echo
echo "📁 Important Files:"
echo "   Environment:      .env"
echo "   Nginx Config:     nginx/nginx.conf"
echo "   Database Data:    mysql_data (Docker volume)"
echo
log_warning "Next Steps:"
echo "1. Test your application at http://$VPS_IP"
echo "2. Configure your VPS firewall to allow port 80"
echo "3. Update your .env file with production settings"
echo "4. Set up monitoring and backups"
echo "5. Consider using a reverse proxy service for additional security"

# Display firewall configuration help
echo
log_info "VPS Firewall Configuration:"
echo "If using UFW (Ubuntu):"
echo "  sudo ufw allow 80/tcp"
echo "  sudo ufw allow 22/tcp  # SSH access"
echo "  sudo ufw --force enable"
echo
echo "If using iptables:"
echo "  sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT"
echo "  sudo iptables-save > /etc/iptables/rules.v4"

# Display monitoring commands
echo
log_info "Monitoring Commands:"
echo "  Check resource usage: docker stats"
echo "  View application logs: docker-compose logs -f backend frontend"
echo "  Check disk space: df -h"
echo "  Monitor network: netstat -tulpn | grep :80"
