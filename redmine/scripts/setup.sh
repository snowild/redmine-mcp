#!/bin/bash

echo "🚀 Starting Redmine development environment..."

# Start Docker services
echo "📦 Starting Docker containers..."
cd "$(dirname "$0")/../docker"
docker-compose up -d

echo "⏳ Waiting for Redmine to start (about 60 seconds)..."
sleep 60

# Check if Redmine is running
echo "🔍 Checking Redmine status..."
until curl -f http://localhost:3000 > /dev/null 2>&1; do
    echo "Waiting for Redmine to fully start..."
    sleep 5
done

echo "✅ Redmine is running!"
echo ""
echo "📋 Redmine Information:"
echo "   - URL: http://localhost:3000"
echo "   - Default admin username: admin"
echo "   - Default password: admin"
echo ""
echo "🔧 Next setup steps:"
echo "1. Open browser and go to http://localhost:3000"
echo "2. Log in with admin/admin"
echo "3. Go to My Account > API Access Key"
echo "4. Click 'Show' to get the API key"
echo "5. Create test projects and issues"
echo ""
echo "💡 Or run the following command for automatic setup:"
echo "   python configure.py"
