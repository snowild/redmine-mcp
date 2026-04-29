#!/usr/bin/env python3
"""
Manual API key setup and testing script
Use this script when automatic configuration fails
"""

import requests
import json
import sys
import os

def test_api_connection(api_key: str, domain: str = "http://localhost:3000") -> bool:
    """Test API connection"""
    print(f"🔍 Testing API key: {api_key[:8]}...")
    
    headers = {
        'X-Redmine-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Test getting project list
        response = requests.get(f"{domain}/projects.json", headers=headers, timeout=10)
        print(f"📡 API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            project_count = len(data.get('projects', []))
            print(f"✅ API connection successful, found {project_count} projects")
            return True
        elif response.status_code == 401:
            print("❌ Invalid API key (401 Unauthorized)")
        elif response.status_code == 403:
            print("❌ API access forbidden (403 Forbidden)")
        elif response.status_code == 422:
            print("❌ API format error (422 Unprocessable Entity)")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    
    return False

def create_test_project(api_key: str, domain: str = "http://localhost:3000") -> bool:
    """Create test project"""
    print("📁 Trying to create test project...")
    
    headers = {
        'X-Redmine-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    project_data = {
        'project': {
            'name': 'Manual Test Project',
            'identifier': 'manual-test',
            'description': 'Manually created test project',
            'is_public': True
        }
    }
    
    try:
        response = requests.post(f"{domain}/projects.json", headers=headers, json=project_data, timeout=10)
        print(f"📡 Create project response: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            project_id = data['project']['id']
            print(f"✅ Test project created successfully (ID: {project_id})")
            return True
        else:
            print(f"❌ Project creation failed: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    
    return False

def update_env_file(api_key: str):
    """Update .env file"""
    env_content = f"""# Redmine MCP test environment configuration
REDMINE_DOMAIN=http://localhost:3000
REDMINE_API_KEY={api_key}
REDMINE_TIMEOUT=30
DEBUG_MODE=true
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file updated")

def main():
    print("🔧 Manual API Key Setup Tool")
    print("=" * 40)
    
    # Check if API key is provided
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manual_api_setup.py <API_KEY>")
        print("")
        print("Please obtain API key manually:")
        print("1. Open browser and go to: http://localhost:3000")
        print("2. Log in with admin/admin")
        print("3. Go to My Account")
        print("4. Find the API Access Key section")
        print("5. If no key exists, click the Reset button")
        print("6. Copy the key and run:")
        print("   python manual_api_setup.py <your_api_key>")
        return False
    
    api_key = sys.argv[1].strip()
    
    # Validate API key format
    if len(api_key) != 40 or not all(c in '0123456789abcdef' for c in api_key.lower()):
        print("⚠️  API key format is incorrect, should be a 40-character hexadecimal string")
        return False
    
    print(f"🔑 Using API key: {api_key[:8]}...")
    
    # Test API connection
    if not test_api_connection(api_key):
        print("❌ API connection test failed")
        return False
    
    # Try to create test project
    create_test_project(api_key)
    
    # Update environment file
    update_env_file(api_key)
    
    print("\n🎉 Setup complete!")
    print("You can now run:")
    print("  uv run python test_mcp_integration.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
