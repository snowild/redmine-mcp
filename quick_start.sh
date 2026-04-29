#!/bin/bash
#
# Redmine MCP quick start script
# ============================
# 
# This script automatically performs the following steps:
# 1. Check Docker environment
# 2. Start Redmine test environment (http://localhost:3000)
# 3. Create test projects and API key
# 4. Run full MCP functionality tests
#
# Use cases:
# - First-time environment setup for new developers
# - Complete functionality verification before release
# - CI/CD automated testing
# - Verification after environment reset
#
# Execution time: approximately 2-3 minutes
# Prerequisites: Docker, Docker Compose, uv

echo "🚀 Redmine MCP Quick Start"
echo "=" * 50

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed, please install Docker first"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed, please install Docker Compose first"
    exit 1
fi

echo "✅ Docker environment check passed"

# Step 1: Start Redmine
echo ""
echo "🚀 Step 1: Start Redmine environment"
echo "----------------------------------------"
./redmine/scripts/setup.sh

# Step 2: Configure Redmine
echo ""
echo "🔧 Step 2: Configure Redmine test data"
echo "----------------------------------------"
uv run python redmine/scripts/configure.py

if [ $? -ne 0 ]; then
    echo "❌ Redmine configuration failed"
    exit 1
fi

# Step 3: Test MCP integration
echo ""
echo "🧪 Step 3: Run MCP functionality tests"
echo "----------------------------------------"
uv run python tests/scripts/mcp_integration.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All tests completed!"
    echo "----------------------------------------"
    echo "✅ Redmine environment started: http://localhost:3000"
    echo "✅ MCP functionality tests passed"
    echo "✅ Environment is ready for development and testing"
    echo ""
    echo "💡 Next steps:"
    echo "   - Configure and test MCP tools in Claude Code"
    echo "   - Continue developing new MCP features"
    echo "   - Run 'cd redmine/docker && docker-compose down' to shut down the test environment"
else
    echo ""
    echo "❌ MCP tests failed, please check the error messages above"
    exit 1
fi
