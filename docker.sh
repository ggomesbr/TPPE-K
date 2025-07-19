#!/bin/bash

# Hospital Management System - Docker Helper Script
# Optimized for WSL and Debian VPS deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Commands
case "$1" in
    "dev")
        print_info "Starting development environment..."
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    "prod")
        print_info "Starting production environment..."
        docker-compose --profile production up --build -d
        ;;
    "stop")
        print_info "Stopping all containers..."
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
        ;;
    "clean")
        print_warning "Cleaning up containers, images, and volumes..."
        read -p "Are you sure? This will remove all data! (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker-compose -f docker-compose.dev.yml down -v
            docker system prune -af
            print_success "Cleanup completed!"
        else
            print_info "Cleanup cancelled."
        fi
        ;;
    "logs")
        if [ -z "$2" ]; then
            print_info "Showing all logs..."
            docker-compose logs -f
        else
            print_info "Showing logs for $2..."
            docker-compose logs -f "$2"
        fi
        ;;
    "shell")
        if [ -z "$2" ]; then
            print_error "Please specify service: backend, frontend, or mysql"
            exit 1
        fi
        print_info "Opening shell for $2..."
        docker-compose exec "$2" sh
        ;;
    "test")
        print_info "Running tests..."
        docker-compose exec backend python -m pytest
        ;;
    "migrate")
        print_info "Running database migrations..."
        docker-compose exec backend alembic upgrade head
        ;;
    "status")
        print_info "Container status:"
        docker-compose ps
        ;;
    *)
        echo "Hospital Management System - Docker Helper"
        echo ""
        echo "Usage: ./docker.sh [command]"
        echo ""
        echo "Commands:"
        echo "  dev      - Start development environment"
        echo "  prod     - Start production environment"
        echo "  stop     - Stop all containers"
        echo "  clean    - Clean up containers and volumes"
        echo "  logs     - Show logs (optionally for specific service)"
        echo "  shell    - Open shell in container (backend|frontend|mysql)"
        echo "  test     - Run backend tests"
        echo "  migrate  - Run database migrations"
        echo "  status   - Show container status"
        echo ""
        echo "Examples:"
        echo "  ./docker.sh dev"
        echo "  ./docker.sh logs backend"
        echo "  ./docker.sh shell backend"
        ;;
esac
