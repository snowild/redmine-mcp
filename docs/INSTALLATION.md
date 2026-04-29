# Installation Guide

This document provides detailed installation steps and configuration instructions for the Redmine MCP Server.

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Environment Configuration](#environment-configuration)
4. [Claude Code Integration](#claude-code-integration)
5. [Verify Installation](#verify-installation)
6. [Troubleshooting](#troubleshooting)

## 🖥️ System Requirements

### Basic Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.12 or higher
- **Network**: Network connection that can access the Redmine server

### Redmine Server Requirements

- **Redmine Version**: 4.0 or higher (recommended 5.0+)
- **REST API**: REST API functionality must be enabled
- **User Permissions**: User account with API access permissions

### Package Manager

It is recommended to use one of the following package managers:

1. **uv** (recommended) - High-performance Python package manager
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **pip** - Python built-in package manager
   ```bash
   # Usually installed with Python
   python -m pip --version
   ```

## 📦 Installation Methods

### Method 1: Install from Source (Recommended)

#### Step 1: Clone the Project

```bash
# Clone the project repository
git clone https://github.com/your-username/redmine-mcp.git
cd redmine-mcp
```

#### Step 2: Install Dependencies

Using uv (recommended):
```bash
# Create virtual environment and install dependencies
uv sync

# Or install dependencies to existing environment only
uv pip install -e .
```

Using pip:
```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install project
pip install -e .
```

### Method 2: Install via PyPI

```bash
# Using uv
uv pip install redmine-mcp

# Using pip
pip install redmine-mcp
```

### Method 3: Developer Installation

```bash
# Clone project
git clone https://github.com/your-username/redmine-mcp.git
cd redmine-mcp

# Install development dependencies
uv sync --all-extras
# Or
pip install -e ".[dev,test]"
```

## ⚙️ Environment Configuration

### Step 1: Create Environment Configuration File

```bash
# Copy environment variable template
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit the `.env` file:

```env
# Redmine server domain (required)
REDMINE_DOMAIN=https://your-redmine-domain.com

# Redmine API key (required)
REDMINE_API_KEY=your_api_key_here

# API request timeout (optional, default 30 seconds)
REDMINE_TIMEOUT=30

# Debug mode (optional, default false)
DEBUG_MODE=false
```

### Step 3: Get Redmine API Key

#### Method 1: Via Redmine Web Interface

1. Log in to your Redmine system
2. Click the username in the upper right corner
3. Select "My Account"
4. Find "API Access Key" in the right panel
5. Click "Show" or "Reset"
6. Copy the displayed API key

#### Method 2: Contact Administrator

If you cannot see the API access key option:

1. Contact the Redmine system administrator
2. Request to enable the REST API functionality
3. Request an API key be generated for your account

### Step 4: Verify Redmine Configuration

Confirm the Redmine server is properly configured:

#### Check if REST API is Enabled

1. Log in to the Redmine admin interface
2. Go to "Administration" → "Settings" → "API"
3. Confirm "Enable REST web service" is checked
4. Save settings

#### Test API Connection

```bash
# Test API connection using curl
curl -H "X-Redmine-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     https://your-redmine-domain.com/issues.json?limit=1
```

The expected response should contain issue data in JSON format.

## 🔗 Claude Code Integration

### Step 1: Install MCP Server

```bash
# Install as system tool
uv tool install .

# Or using pip
pip install .
```

### Step 2: Add to Claude Code

#### Method 1: Using Command Line

```bash
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here"
```

#### Method 2: Manually Edit Configuration File

Edit Claude Code's MCP configuration file:

**macOS/Linux Location:**
```
~/.config/claude-code/mcp_servers.json
```

**Windows Location:**
```
%APPDATA%\claude-code\mcp_servers.json
```

**Configuration Content:**
```json
{
  "servers": {
    "redmine": {
      "command": "redmine-mcp",
      "env": {
        "REDMINE_DOMAIN": "https://your-redmine-domain.com",
        "REDMINE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Step 3: Restart Claude Code

Restart Claude Code to load the new MCP server configuration.

## ✅ Verify Installation

### Test 1: MCP Server Test

```bash
# Test if MCP server is running normally
uv run python -m redmine_mcp.server

# If you see server startup message without errors, installation is successful
```

### Test 2: Claude Code Integration Test

```bash
# Run Claude Code integration test
uv run python test_claude_integration.py
```

Expected output:
```
✅ MCP server started successfully
✅ Server information retrieved successfully
✅ Health check passed
✅ Tool list loaded successfully (14 tools)
```

### Test 3: Full Functionality Test

```bash
# Run complete MCP functionality test
uv run python test_mcp_integration.py
```

Expected to see all test items pass:
```
📊 Test Results Summary
==================================================
Total Tests: 13
Passed: 13
Failed: 0
Success Rate: 100.0%

🎉 Tests passed! MCP functionality is working normally
```

### Test 4: Manual Test in Claude Code

Enter in Claude Code:

```
Please run health check
```

If you see a response similar to the following, integration is successful:
```
✓ Server is running normally, connected to https://your-redmine-domain.com
```

## 🔧 Troubleshooting

### Common Problem 1: Python Version Incompatibility

**Error Message:**
```
Python 3.12 or higher is required
```

**Solution:**
```bash
# Check Python version
python --version

# If version is too old, please upgrade Python
# macOS using Homebrew
brew install python@3.12

# Ubuntu/Debian
sudo apt update
sudo apt install python3.12

# Windows please download latest version from python.org
```

### Common Problem 2: uv Not Found

**Error Message:**
```
uv: command not found
```

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell configuration
source ~/.bashrc  # Or ~/.zshrc
```

### Common Problem 3: Invalid API Key

**Error Message:**
```
Authentication failed: Please check if the API key is correct
```

**Solution:**
1. Confirm `REDMINE_API_KEY` in `.env` file is correct
2. Check if the API key in Redmine is still valid
3. Confirm the user corresponding to the API key has sufficient permissions

### Common Problem 4: REST API Not Enabled

**Error Message:**
```
Insufficient permissions: You do not have permission to perform this operation
```

**Solution:**
1. Contact the Redmine administrator to confirm REST API is enabled
2. Confirm your user account has API access permissions
3. Check user permission settings in relevant projects

### Common Problem 5: Network Connection Issues

**Error Message:**
```
Connection failed: Please check network connection and Redmine server status
```

**Solution:**
1. Check network connection
2. Confirm Redmine server URL is correct
3. Check firewall settings
4. Try increasing timeout:
   ```env
   REDMINE_TIMEOUT=60
   ```

### Common Problem 6: Claude Code Cannot Load MCP Server

**Solution:**
1. Check if MCP configuration file format is correct
2. Confirm `redmine-mcp` command can be executed in the command line
3. Restart Claude Code
4. Check Claude Code error logs

### Debug Techniques

#### Enable Debug Mode

Set in `.env` file:
```env
DEBUG_MODE=true
```

#### Check Configuration Loading

```bash
# Run configuration check
uv run python -c "
from redmine_mcp.config import get_config
config = get_config()
print(f'Domain: {config.redmine_domain}')
print(f'API Key: {config.redmine_api_key[:10]}...')
print(f'Timeout: {config.redmine_timeout}')
"
```

#### Manually Test API Connection

```bash
# Run connection test script
uv run python debug_auth.py
```

## 🔄 Upgrade Guide

### Upgrading from Old Version

```bash
# Update source code
git pull origin main

# Update dependencies
uv sync

# Or using pip
pip install -e . --upgrade
```

### Check Configuration Compatibility

After upgrading, please check:
1. Whether `.env` file format needs to be updated
2. Whether the new version has new configuration options
3. Whether Claude Code MCP configuration needs adjustment

## 📖 Next Steps

After installation is complete, it is recommended to read:

1. [Usage Examples](USAGE_EXAMPLES.md) - Learn how to use various features
2. [API Reference](API_REFERENCE.md) - Detailed tool parameter descriptions
3. [README.md](../README.md) - Project overview and quick start

If you have any installation issues, feel free to open an Issue for assistance.
