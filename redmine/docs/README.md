# Redmine Test Environment Guide

This directory contains all Redmine-related settings and management tools for the Redmine MCP project.

## 📁 Directory Structure

```
redmine/
├── docker/                    # Docker-related settings
│   ├── docker-compose.yml     # MySQL 8.0 + Redmine 5.1 container configuration
│   └── init/                  # Docker initialization script directory
├── scripts/                   # Configuration and management scripts
│   ├── setup.sh              # Start Redmine environment
│   ├── configure.py           # Auto-create test data and API key
│   ├── manual_api_setup.py    # Manual API setup and testing
│   └── enable_rest_api.py     # Enable REST API functionality
├── docs/                      # Setup documentation
│   ├── README.md             # This file - overview
│   ├── setup.md              # Detailed setup steps
│   └── api.md                # API usage guide
└── configs/                   # Configuration templates
    └── .env.example          # Environment variable examples
```

## 🚀 Quick Start

### One-Click Start (Recommended)

```bash
# Run from project root
./redmine/scripts/setup.sh
```

### Complete Setup Process

```bash
# 1. Start Redmine environment
./redmine/scripts/setup.sh

# 2. Auto-configure test data
cd redmine/scripts
python configure.py

# 3. Test API connection
python manual_api_setup.py
```

## 🌐 Service Information

### Redmine Instance
- **URL**: http://localhost:3000
- **Admin username**: admin
- **Admin password**: admin
- **Version**: Redmine 5.1

### Database
- **Type**: MySQL 8.0
- **Container name**: redmine-mysql
- **Internal port**: 3306

### Docker Containers
- **redmine-app**: Redmine application service (port 3000)
- **redmine-mysql**: MySQL database service

## 📝 Configuration Guide

### Environment Variables
Refer to `configs/.env.example` to create your `.env` file:

```bash
# Copy example file
cp redmine/configs/.env.example .env

# Edit configuration
vim .env
```

### Test Data
The auto-configuration script will create:
- 3 test projects
- 5 test issues per project
- API key configuration

## 🔧 Management Commands

### Environment Control
```bash
# Start services
cd redmine/docker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs redmine

# Stop services
docker-compose down

# Full cleanup (including data)
docker-compose down -v
```

### Reconfigure
```bash
# Reset Redmine environment
cd redmine/docker
docker-compose down -v
cd ../scripts
./setup.sh
```

## 🧪 Testing and Verification

### API Connection Test
```bash
cd redmine/scripts
python manual_api_setup.py
```

### MCP Functionality Test
```bash
# Run from project root
python tests/scripts/mcp_integration.py
```

## 📚 More Documentation

- [Detailed Setup Steps](setup.md) - Complete environment setup guide
- [API Usage Guide](api.md) - Redmine REST API reference

## ⚠️ Notes

- This environment is for development and testing only
- First startup takes about 60-90 seconds for database initialization
- Please ensure port 3000 is not used by other services
- Please remember to stop Docker containers after testing to save resources
