# Hospital Management System - Docker Helper Script for Windows
param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    [string]$Service = ""
)

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

switch ($Command.ToLower()) {
    "dev" {
        Write-Info "Starting development environment..."
        docker-compose -f docker-compose.dev.yml up --build
    }
    "prod" {
        Write-Info "Starting production environment..."
        docker-compose --profile production up --build -d
    }
    "stop" {
        Write-Info "Stopping all containers..."
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
    }
    "clean" {
        Write-Warning "Cleaning up containers, images, and volumes..."
        $confirmation = Read-Host "Are you sure? This will remove all data! (y/N)"
        if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
            docker-compose down -v
            docker-compose -f docker-compose.dev.yml down -v
            docker system prune -af
            Write-Success "Cleanup completed!"
        } else {
            Write-Info "Cleanup cancelled."
        }
    }
    "logs" {
        if ([string]::IsNullOrEmpty($Service)) {
            Write-Info "Showing all logs..."
            docker-compose logs -f
        } else {
            Write-Info "Showing logs for $Service..."
            docker-compose logs -f $Service
        }
    }
    "shell" {
        if ([string]::IsNullOrEmpty($Service)) {
            Write-Error-Custom "Please specify service: backend, frontend, or mysql"
            exit 1
        }
        Write-Info "Opening shell for $Service..."
        docker-compose exec $Service sh
    }
    "test" {
        Write-Info "Running tests..."
        docker-compose exec backend python -m pytest
    }
    "migrate" {
        Write-Info "Running database migrations..."
        docker-compose exec backend alembic upgrade head
    }
    "status" {
        Write-Info "Container status:"
        docker-compose ps
    }
    default {
        Write-Host "Hospital Management System - Docker Helper" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage: .\docker.ps1 -Command [command] [-Service service]" -ForegroundColor White
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor White
        Write-Host "  dev      - Start development environment" -ForegroundColor Gray
        Write-Host "  prod     - Start production environment" -ForegroundColor Gray
        Write-Host "  stop     - Stop all containers" -ForegroundColor Gray
        Write-Host "  clean    - Clean up containers and volumes" -ForegroundColor Gray
        Write-Host "  logs     - Show logs (optionally for specific service)" -ForegroundColor Gray
        Write-Host "  shell    - Open shell in container (backend|frontend|mysql)" -ForegroundColor Gray
        Write-Host "  test     - Run backend tests" -ForegroundColor Gray
        Write-Host "  migrate  - Run database migrations" -ForegroundColor Gray
        Write-Host "  status   - Show container status" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Yellow
        Write-Host "  .\docker.ps1 -Command dev" -ForegroundColor Green
        Write-Host "  .\docker.ps1 -Command logs -Service backend" -ForegroundColor Green
        Write-Host "  .\docker.ps1 -Command shell -Service backend" -ForegroundColor Green
    }
}
