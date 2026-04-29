# Redmine Environment Setup Detailed Guide

This document provides detailed setup steps and troubleshooting instructions for the Redmine test environment.

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, Windows (with WSL2)
- **Memory**: At least 2GB available
- **Disk Space**: At least 1GB
- **Network**: Internet connection required to download Docker images

### Required Software
- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0 (or docker-compose >= 1.29)
- **Python**: >= 3.8 (for setup scripts)
- **curl**: for health checks

### Check Installation
```bash
# Check Docker
docker --version
docker-compose --version  # or docker compose version

# Check Python
python3 --version

# Check curl
curl --version
```

## 🚀 Installation Steps

### Step 1: Prepare Environment

```bash
# Ensure no other service is using port 3000
lsof -i :3000

# If a service is running, stop it
sudo kill -9 $(lsof -ti:3000)
```

### Step 2: Start Redmine

```bash
# Method 1: Use convenient script (recommended)
./redmine/scripts/setup.sh

# Method 2: Manual start
cd redmine/docker
docker-compose up -d
```

### Step 3: Verify Startup

```bash
# Check container status
docker-compose ps

# Check Redmine logs
docker-compose logs redmine

# Test web interface
curl -I http://localhost:3000
```

Expected output:
```
HTTP/1.1 200 OK
```

### Step 4: Initial Setup

#### 4.1 Web Interface Setup
1. Open browser and go to http://localhost:3000
2. Log in with username/password `admin` / `admin`
3. You will be asked to change password on first login (can be skipped)

#### 4.2 API Setup
```bash
# Automatic setup (recommended)
cd redmine/scripts
python configure.py

# Manual setup
python manual_api_setup.py
```

### Step 5: Create Test Data

The auto-configuration script will create:
- **MCP Test Project** (`mcp-test`)
- **Software Development** (`software-dev`)
- **Bug Tracking** (`bug-tracking`)

Each project contains 5 test issues of different statuses.

## ⚙️ Detailed Configuration

### Docker Compose Description

```yaml
# redmine/docker/docker-compose.yml
version: '3.8'

services:
  redmine-db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: redmine
      MYSQL_USER: redmine
      MYSQL_PASSWORD: redmine_password
    volumes:
      - redmine_db_data:/var/lib/mysql
      
  redmine:
    image: redmine:5.1
    ports:
      - "3000:3000"
    environment:
      REDMINE_DB_MYSQL: redmine-db
      REDMINE_DB_USERNAME: redmine
      REDMINE_DB_PASSWORD: redmine_password
      REDMINE_DB_DATABASE: redmine
      REDMINE_SECRET_KEY_BASE: supersecretkey
    volumes:
      - redmine_data:/usr/src/redmine/files
      - redmine_plugins:/usr/src/redmine/plugins
      - ./init:/docker-entrypoint-initdb.d
```

### Environment Variable Setup

```bash
# Copy example configuration
cp redmine/configs/.env.example .env

# Edit configuration (optional)
vim .env
```

Example content:
```bash
REDMINE_DOMAIN=http://localhost:3000
REDMINE_API_KEY=your_api_key_here
REDMINE_MCP_TIMEOUT=30
REDMINE_MCP_LOG_LEVEL=INFO
```

## 🔧 Advanced Settings

### Change Port

If port 3000 is occupied:

```yaml
# Edit redmine/docker/docker-compose.yml
services:
  redmine:
    ports:
      - "3001:3000"  # Change to another port
```

The corresponding environment variable also needs to be updated:
```bash
REDMINE_DOMAIN=http://localhost:3001
```

### Data Persistence

Docker volumes are automatically created:
- `redmine_db_data`: Database data
- `redmine_data`: Redmine files
- `redmine_plugins`: Redmine plugins

### Custom Initialization

Place initialization scripts in the `redmine/docker/init/` directory:
```bash
# Example: create initial user
echo "CREATE USER 'testuser'@'%' IDENTIFIED BY 'testpass';" > redmine/docker/init/01-users.sql
```

## 🐛 Troubleshooting

### Common Issues

#### Q1: Docker container fails to start
```bash
# Check Docker service status
docker info

# Check port usage
lsof -i :3000

# View detailed errors
docker-compose logs
```

#### Q2: Redmine startup takes too long
```bash
# Normal startup takes 60-90 seconds, you can check progress
docker-compose logs -f redmine
```

Expected startup logs:
```
redmine-app | => Booting WEBrick
redmine-app | => Rails 6.1.4 application starting
redmine-app | => Creating database
redmine-app | => Migrating database
redmine-app | => Rails application started on 0.0.0.0:3000
```

#### Q3: Cannot connect to Redmine
```bash
# Check container status
docker-compose ps

# Test network connection
curl -v http://localhost:3000

# Check firewall settings (macOS)
sudo pfctl -s all
```

#### Q4: API setup failed
```bash
# Get API key manually
# 1. Log in to http://localhost:3000
# 2. Go to My Account > API Access Key
# 3. Click 'Show'

# Test API connection
python redmine/scripts/manual_api_setup.py
```

#### Q5: Database connection error
```bash
# Check MySQL container
docker-compose logs redmine-db

# Restart MySQL container
docker-compose restart redmine-db

# Full rebuild
docker-compose down -v
docker-compose up -d
```

### Log Analysis

#### View all service logs
```bash
docker-compose logs
```

#### View specific service logs
```bash
# Redmine application logs
docker-compose logs redmine

# MySQL database logs
docker-compose logs redmine-db

# Follow logs in real-time
docker-compose logs -f redmine
```

### Performance Tuning

#### Allocate More Memory
```yaml
# Edit docker-compose.yml
services:
  redmine:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

#### Use SSD Storage
```bash
# Ensure Docker data is on SSD
docker info | grep "Docker Root Dir"
```

## 🔄 Reset Environment

### Full Reset
```bash
# Stop and delete all containers and data
cd redmine/docker
docker-compose down -v

# Clean up Docker resources
docker system prune -f

# Restart
cd ../scripts
./setup.sh
```

### Restart with Data Preserved
```bash
cd redmine/docker
docker-compose restart
```

### Rebuild Only Redmine Container
```bash
cd redmine/docker
docker-compose up -d --force-recreate redmine
```

## 📊 Health Check

Create health check script:
```bash
#!/bin/bash
# redmine/scripts/health_check.sh

echo "🔍 Redmine Health Check"
echo "======================="

# Check container status
echo "📦 Container status:"
docker-compose -f redmine/docker/docker-compose.yml ps

# Check network connection
echo ""
echo "🌐 Network connection:"
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Redmine web interface is normal"
else
    echo "❌ Redmine web interface cannot be connected"
fi

# Check API
echo ""
echo "🔌 API connection:"
if [ -f .env ]; then
    source .env
    if [ ! -z "$REDMINE_API_KEY" ]; then
        if curl -s -H "X-Redmine-API-Key: $REDMINE_API_KEY" http://localhost:3000/projects.json > /dev/null; then
            echo "✅ Redmine API is normal"
        else
            echo "❌ Redmine API cannot be connected"
        fi
    else
        echo "⚠️  API key not set"
    fi
else
    echo "⚠️  .env file does not exist"
fi
```

## 🚀 Automated Deployment

Create automated deployment script:
```bash
#!/bin/bash
# redmine/scripts/deploy.sh

set -e

echo "🚀 Automated Redmine Deployment"
echo "====================="

# Check prerequisites
./redmine/scripts/health_check.sh

# Start environment
./redmine/scripts/setup.sh

# Configure data
cd redmine/scripts
python configure.py

# Verify installation
python manual_api_setup.py

echo "✅ Redmine environment deployment complete!"
```

## 📝 Development Workflow

### Daily Development
```bash
# 1. Start environment
./redmine/scripts/setup.sh

# 2. Develop MCP features
vim src/redmine_mcp/server.py

# 3. Test features
python tests/scripts/mcp_integration.py

# 4. Stop environment
cd redmine/docker
docker-compose down
```

### Version Upgrade
```bash
# 1. Backup data
docker run --rm -v redmine_db_data:/source -v $(pwd):/backup alpine tar czf /backup/redmine_backup.tar.gz -C /source .

# 2. Update image version
# Edit docker-compose.yml version number

# 3. Rebuild services
docker-compose down
docker-compose pull
docker-compose up -d
```
