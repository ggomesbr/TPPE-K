# Hospital Management System - VPS HTTP Deployment Guide

## 🚀 Simple VPS Deployment (HTTP-only with IP access)

This guide will help you deploy the Hospital Management System on a VPS using only HTTP and IP address access (no domain or SSL required).

## 📋 Prerequisites

- VPS with Ubuntu 20.04+ or similar Linux distribution
- At least 2GB RAM and 20GB storage
- SSH access to your VPS
- VPS public IP address

## 🔧 Quick Deployment Steps

### 1. Prepare Your VPS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install -y git

# Logout and login again for Docker group to take effect
exit
```

### 2. Configure Firewall

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw --force enable

# Check firewall status
sudo ufw status
```

### 3. Clone and Deploy

```bash
# Clone your repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Run the deployment script with your VPS IP
./deploy-vps.sh YOUR_VPS_IP_ADDRESS

# Example:
# ./deploy-vps.sh 203.0.113.10
```

### 4. Verify Deployment

```bash
# Check if all services are running
docker-compose ps

# Check application health
curl http://YOUR_VPS_IP/health

# View logs if needed
docker-compose logs -f
```

## 🌐 Access Your Application

After successful deployment, access your application at:

- **Frontend**: `http://YOUR_VPS_IP`
- **API**: `http://YOUR_VPS_IP/api`
- **Health Check**: `http://YOUR_VPS_IP/health`

### Login Credentials

Use the demo credentials provided in the login page:
- **Email**: `joao.silva@hospital.com`
- **Password**: `senha123456`

## 🔄 Management Commands

### View Application Status
```bash
docker-compose ps
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Update Application
```bash
git pull origin main
docker-compose down
docker-compose up --build -d
```

### Stop Services
```bash
docker-compose down
```

### Backup Database
```bash
# Create backup
docker-compose exec mysql mysqldump -u hospital_user -p hospital_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup (if needed)
docker-compose exec -T mysql mysql -u hospital_user -p hospital_db < backup_file.sql
```

## 🛡️ Security Considerations

### 1. Firewall Configuration
- Only port 80 (HTTP) and 22 (SSH) are open
- Consider changing SSH port from default 22
- Use strong SSH keys instead of passwords

### 2. Application Security
- Strong database passwords are auto-generated
- API rate limiting is configured
- Security headers are set

### 3. VPS Security
```bash
# Change SSH port (optional)
sudo nano /etc/ssh/sshd_config
# Change: Port 22 to Port 2222
sudo systemctl restart ssh

# Install fail2ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## 📊 Monitoring

### Check Resource Usage
```bash
# Container resource usage
docker stats

# System resources
htop
df -h
free -h
```

### View Application Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Monitor Network
```bash
# Check open ports
sudo netstat -tulpn | grep :80
sudo ss -tulpn | grep :80

# Check connections
sudo netstat -an | grep :80
```

## 🆘 Troubleshooting

### Common Issues

1. **Cannot access application from browser**
   - Check if firewall allows port 80: `sudo ufw status`
   - Check if services are running: `docker-compose ps`
   - Check if VPS IP is correct

2. **502 Bad Gateway**
   - Check backend service: `docker-compose logs backend`
   - Restart services: `docker-compose restart`

3. **Database connection issues**
   - Check MySQL container: `docker-compose logs mysql`
   - Verify environment variables in `.env`

4. **Out of disk space**
   - Check disk usage: `df -h`
   - Clean Docker images: `docker system prune -a`

### Debug Commands

```bash
# Check container status
docker-compose ps

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec mysql bash

# Test network connectivity
docker-compose exec backend ping mysql
docker-compose exec nginx ping backend

# Check container logs
docker-compose logs [service_name]
```

## 💡 Performance Tips

### 1. Optimize VPS Resources
```bash
# Increase swap if needed (for low memory VPS)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. Docker Optimization
```bash
# Clean unused Docker resources periodically
docker system prune -f

# Remove unused images
docker image prune -a -f
```

## 🔄 Backup Strategy

### Automated Database Backup
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/$USER/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec mysql mysqldump -u hospital_user -p$MYSQL_PASSWORD hospital_db > "$BACKUP_DIR/db_backup_$DATE.sql"

# Keep only last 7 backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_backup_$DATE.sql"
EOF

chmod +x backup.sh

# Add to crontab for daily backup at 2 AM
(crontab -l ; echo "0 2 * * * /home/$USER/your-repo/backup.sh") | crontab -
```

## 📞 Support

For issues and support:
1. Check the troubleshooting section above
2. Review application logs: `docker-compose logs -f`
3. Check system resources: `htop` and `df -h`
4. Create an issue in the project repository

---

**Note**: This deployment uses HTTP only and is suitable for development, testing, or internal use. For production with external users, consider using a domain with SSL/HTTPS.
