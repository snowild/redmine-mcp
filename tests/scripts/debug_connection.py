#!/usr/bin/env python3
"""
Debug Redmine connection issues
"""

import sys
import os
from pathlib import Path
import requests

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def debug_connection():
    """Debug connection issues in detail"""
    print("🔍 Debugging Redmine connection")
    print("=" * 50)
    
    try:
        from redmine_mcp.config import get_config
        config = get_config()
        
        print(f"Domain: {config.redmine_domain}")
        print(f"API Key: {config.redmine_api_key[:8]}...{config.redmine_api_key[-4:]}")
        print(f"Timeout: {config.redmine_timeout}")
        
        # Test basic HTTP connection
        print("\n1️⃣ Testing basic HTTP connection...")
        try:
            response = requests.get(config.redmine_domain, timeout=10)
            print(f"✅ HTTP connection successful (status code: {response.status_code})")
        except Exception as e:
            print(f"❌ HTTP connection failed: {e}")
            return
        
        # Test API endpoint
        print("\n2️⃣ Testing API endpoint...")
        api_url = f"{config.redmine_domain}/my/account.json"
        headers = {'X-Redmine-API-Key': config.redmine_api_key}
        
        try:
            response = requests.get(api_url, headers=headers, timeout=config.redmine_timeout)
            print(f"API response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'user' in data:
                    user = data['user']
                    print(f"✅ API authentication successful")
                    print(f"  User: {user.get('login', 'N/A')} ({user.get('firstname', '')} {user.get('lastname', '')})")
                else:
                    print(f"❌ API response format abnormal: {data}")
            elif response.status_code == 401:
                print(f"❌ API key invalid (401 Unauthorized)")
            elif response.status_code == 403:
                print(f"❌ Insufficient permissions (403 Forbidden)")
            elif response.status_code == 404:
                print(f"❌ API endpoint does not exist (404 Not Found)")
            else:
                print(f"❌ Unknown error ({response.status_code})")
                print(f"Response content: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout ({config.redmine_timeout}s)")
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error")
        except Exception as e:
            print(f"❌ API request failed: {e}")
        
        # Test other API endpoints
        print("\n3️⃣ Testing other API endpoints...")
        endpoints = [
            ('/issues.json?limit=1', 'Issue list'),
            ('/projects.json?limit=1', 'Project list'),
            ('/enumerations/issue_priorities.json', 'Priority list'),
        ]
        
        for endpoint, desc in endpoints:
            try:
                url = f"{config.redmine_domain}{endpoint}"
                response = requests.get(url, headers=headers, timeout=config.redmine_timeout)
                if response.status_code == 200:
                    print(f"✅ {desc}: {response.status_code}")
                else:
                    print(f"⚠️ {desc}: {response.status_code}")
            except Exception as e:
                print(f"❌ {desc}: {e}")
        
        # Test our client
        print("\n4️⃣ Testing client...")
        try:
            from redmine_mcp.redmine_client import get_client
            client = get_client()
            
            # Directly test _make_request method
            response = client._make_request('GET', '/my/account.json')
            if 'user' in response:
                print(f"✅ Client request successful")
            else:
                print(f"❌ Client request abnormal: {response}")
                
        except Exception as e:
            print(f"❌ Client test failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Debug process failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_connection()
