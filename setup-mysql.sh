#!/bin/bash

# Hospital Management System - MySQL Setup Script
echo "🏥 Hospital Management System - MySQL Configuration"
echo "================================================="

# Function to start with Docker Compose
start_with_docker() {
    echo "🐳 Starting MySQL with Docker Compose..."
    
    # Update .env for Docker
    sed -i 's/MYSQL_HOST=localhost/MYSQL_HOST=mysql/' .env
    echo "RUNNING_IN_DOCKER=true" >> .env
    
    # Start MySQL and Backend
    docker-compose up -d mysql
    
    echo "⏳ Waiting for MySQL to be ready..."
    sleep 10
    
    # Check if MySQL is ready
    until docker-compose exec mysql mysqladmin ping -h localhost --silent; do
        echo "Waiting for MySQL..."
        sleep 2
    done
    
    echo "✅ MySQL is ready!"
    echo "📊 Database URL: mysql+pymysql://hospital_user:hospital_pass123@localhost:3306/hospital_db"
    echo "🔗 Access MySQL: docker-compose exec mysql mysql -u hospital_user -p hospital_db"
    echo "🚀 Start backend: docker-compose up backend"
}

# Function to install MySQL locally
install_mysql_local() {
    echo "💻 Installing MySQL locally..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install mysql-server mysql-client -y
        sudo systemctl start mysql
        sudo systemctl enable mysql
    elif command -v yum &> /dev/null; then
        # RHEL/CentOS
        sudo yum install mysql-server mysql -y
        sudo systemctl start mysqld
        sudo systemctl enable mysqld
    elif command -v brew &> /dev/null; then
        # macOS
        brew install mysql
        brew services start mysql
    else
        echo "❌ Unsupported system. Please install MySQL manually."
        exit 1
    fi
    
    echo "✅ MySQL installed locally"
}

# Function to setup local MySQL database
setup_local_database() {
    echo "🗄️ Setting up local MySQL database..."
    
    # Update .env for local MySQL
    sed -i 's/MYSQL_HOST=mysql/MYSQL_HOST=localhost/' .env
    sed -i '/RUNNING_IN_DOCKER/d' .env
    
    # Create database and user
    mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'hospital_user'@'localhost' IDENTIFIED BY 'hospital_pass123';
GRANT ALL PRIVILEGES ON hospital_db.* TO 'hospital_user'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    echo "✅ Database and user created"
    echo "📊 Database URL: mysql+pymysql://hospital_user:hospital_pass123@localhost:3306/hospital_db"
}

# Main menu
echo "Choose MySQL setup option:"
echo "1. Docker Compose (Recommended for development)"
echo "2. Local MySQL installation"
echo "3. Use existing MySQL"
echo "4. Keep SQLite (current)"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        start_with_docker
        ;;
    2)
        install_mysql_local
        setup_local_database
        ;;
    3)
        echo "🔧 Using existing MySQL..."
        echo "Make sure to update .env with your MySQL credentials"
        setup_local_database
        ;;
    4)
        echo "📁 Keeping SQLite configuration"
        sed -i 's/^MYSQL_DATABASE=/#MYSQL_DATABASE=/' .env
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 MySQL configuration complete!"
echo "🚀 To start the backend:"
echo "   cd backend && uvicorn src.main:app --reload"
echo ""
echo "📖 To access API docs: http://localhost:8000/docs"
