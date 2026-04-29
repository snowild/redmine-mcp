#!/usr/bin/env python3
"""
Redmine auto-configuration script
Used to create test projects, issues, and users
"""

import requests
import json
import time
import sys
import re
from typing import Optional


class RedmineConfigurator:
    def __init__(self, url: str = "http://localhost:3000", username: str = "admin", password: str = "admin"):
        self.url = url.rstrip('/')
        self.session = requests.Session()
        self.api_key: Optional[str] = None
        
        # Login to obtain API key
        self._login(username, password)
    
    def _login(self, username: str, password: str):
        """Login and obtain API key"""
        print(f"🔐 Logging in to Redmine ({username})...")
        
        # First, get CSRF token
        response = self.session.get(f"{self.url}/login")
        if response.status_code != 200:
            raise Exception(f"Cannot access Redmine: {response.status_code}")
        
        # Parse CSRF token
        csrf_match = re.search(r'name="authenticity_token" value="([^"]+)"', response.text)
        if not csrf_match:
            raise Exception("CSRF token not found")
        
        csrf_token = csrf_match.group(1)
        
        # Perform login
        login_data = {
            'username': username,
            'password': password,
            'authenticity_token': csrf_token
        }
        
        response = self.session.post(f"{self.url}/login", data=login_data, allow_redirects=False)
        
        if response.status_code not in [302, 200]:
            raise Exception(f"Login failed: {response.status_code}")
        
        print("✅ Login successful")
        
        # Get or create API key
        self._get_or_create_api_key()
    
    def _get_or_create_api_key(self):
        """Get or create API key"""
        print("🔑 Obtaining API key...")
        
        # Go to my account page
        response = self.session.get(f"{self.url}/my/account")
        if response.status_code != 200:
            print(f"⚠️  Cannot access account page: {response.status_code}")
            self._use_fallback_api_key()
            return
            
        # Print partial response content for debugging
        print(f"📄 Account page response length: {len(response.text)} characters")
        
        # Look for existing API key (supports Chinese and English interfaces)
        api_patterns = [
            r'API access key.*?([a-f0-9]{40})',
            r'API access key.*?([a-f0-9]{40})',
            r'api.*?key.*?([a-f0-9]{40})',
            r'([a-f0-9]{40})'  # any 40-char hex string
        ]
        
        for pattern in api_patterns:
            key_match = re.search(pattern, response.text, re.IGNORECASE | re.DOTALL)
            if key_match:
                self.api_key = key_match.group(1)
                print(f"✅ Found existing API key: {self.api_key[:8]}...")
                return
        
        # If not found, try to reset API key
        print("🔄 Trying to reset API key...")
        csrf_match = re.search(r'name="authenticity_token" value="([^"]+)"', response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"🎫 Found CSRF token: {csrf_token[:8]}...")
            
            # Try to reset API key
            reset_endpoints = [
                f"{self.url}/my/api_key",
                f"{self.url}/my/account/reset_api_key"
            ]
            
            for endpoint in reset_endpoints:
                try:
                    reset_data = {
                        'authenticity_token': csrf_token,
                        '_method': 'post'
                    }
                    reset_response = self.session.post(endpoint, data=reset_data, allow_redirects=True)
                    print(f"🔄 Reset request response: {reset_response.status_code}")
                    
                    if reset_response.status_code in [200, 302]:
                        # Re-fetch account page
                        time.sleep(1)  # Wait one second
                        account_response = self.session.get(f"{self.url}/my/account")
                        
                        # Search for API key again
                        for pattern in api_patterns:
                            key_match = re.search(pattern, account_response.text, re.IGNORECASE | re.DOTALL)
                            if key_match:
                                self.api_key = key_match.group(1)
                                print(f"✅ API key obtained after reset: {self.api_key[:8]}...")
                                return
                                
                        break  # If request succeeded but key not found, don't try other endpoints
                except Exception as e:
                    print(f"⚠️  Reset endpoint {endpoint} failed: {e}")
                    continue
        else:
            print("⚠️  CSRF token not found")
        
        # If all methods fail, use manual prompt
        self._use_fallback_api_key()
    
    def _use_fallback_api_key(self):
        """Use fallback API key setting"""
        print("⚠️  Automatic API key acquisition failed")
        print("📝 Please obtain API key manually:")
        print("   1. Open browser and go to: http://localhost:3000")
        print("   2. Log in with admin/admin")
        print("   3. Go to My Account -> API Access Key")
        print("   4. If no key exists, click the Reset button")
        print("   5. Copy the API key and update the .env file")
        
        # Use test key for subsequent testing
        self.api_key = "test_api_key_for_development_only_123456789"
        print(f"🔧 Temporarily using test key: {self.api_key[:8]}...")
    
    def _api_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Send API request"""
        headers = {
            'X-Redmine-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.url}/{endpoint.lstrip('/')}"
        
        if method.upper() == 'GET':
            response = self.session.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = self.session.post(url, headers=headers, json=data)
        elif method.upper() == 'PUT':
            response = self.session.put(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code not in [200, 201]:
            print(f"API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {}
        
        try:
            return response.json() if response.content else {}
        except:
            return {}
    
    def create_test_project(self, name: str, identifier: str, description: str = "") -> Optional[int]:
        """Create test project"""
        print(f"📁 Creating project: {name}")
        
        project_data = {
            'project': {
                'name': name,
                'identifier': identifier,
                'description': description,
                'is_public': True
            }
        }
        
        response = self._api_request('POST', '/projects.json', project_data)
        
        if 'project' in response:
            project_id = response['project']['id']
            print(f"✅ Project created successfully (ID: {project_id})")
            return project_id
        else:
            print(f"❌ Project creation failed")
            return None
    
    def create_test_issue(self, project_id: int, subject: str, description: str = "") -> Optional[int]:
        """Create test issue"""
        print(f"📝 Creating issue: {subject}")
        
        issue_data = {
            'issue': {
                'project_id': project_id,
                'subject': subject,
                'description': description
            }
        }
        
        response = self._api_request('POST', '/issues.json', issue_data)
        
        if 'issue' in response:
            issue_id = response['issue']['id']
            print(f"✅ Issue created successfully (ID: {issue_id})")
            return issue_id
        else:
            print(f"❌ Issue creation failed")
            return None
    
    def setup_test_data(self):
        """Set up test data"""
        print("🎯 Setting up test data...")
        
        # Create test projects
        projects = [
            ("MCP Test Project", "mcp-test", "Project for testing Redmine MCP integration"),
            ("Software Development", "software-dev", "Software development related project"),
            ("Bug Tracking", "bug-tracking", "Bug tracking and resolution project")
        ]
        
        created_projects = []
        for name, identifier, description in projects:
            project_id = self.create_test_project(name, identifier, description)
            if project_id:
                created_projects.append((project_id, name))
        
        # Create test issues for each project
        test_issues = [
            ("Fix login issue", "Users report inability to log in with correct credentials"),
            ("Add search feature", "Add full-text search functionality to the main page"),
            ("Performance optimization", "Homepage loading time is too long, needs performance optimization"),
            ("UI improvement", "Update user interface design to improve user experience"),
            ("Security check", "Perform system security checks and vulnerability fixes")
        ]
        
        for project_id, project_name in created_projects:
            print(f"\n📋 Creating issues for project '{project_name}'...")
            for subject, description in test_issues:
                self.create_test_issue(project_id, f"[{project_name}] {subject}", description)
        
        return created_projects
    
    def get_api_key(self) -> str:
        """Get API key"""
        return self.api_key


def main():
    print("🔧 Redmine Auto-Configuration Tool")
    print("=" * 40)
    
    try:
        # Wait for Redmine to start
        print("⏳ Checking if Redmine is running...")
        import time
        for i in range(30):
            try:
                response = requests.get("http://localhost:3000", timeout=5)
                if response.status_code == 200:
                    break
            except:
                pass
            print(f"Waiting... ({i+1}/30)")
            time.sleep(2)
        else:
            print("❌ Redmine is not running, please run ./setup_redmine.sh first")
            return False
        
        print("✅ Redmine is running")
        
        # Configure Redmine
        configurator = RedmineConfigurator()
        created_projects = configurator.setup_test_data()
        api_key = configurator.get_api_key()
        
        print("\n🎉 Redmine setup complete!")
        print("=" * 40)
        print(f"📍 Redmine URL: http://localhost:3000")
        print(f"🔑 API Key: {api_key}")
        print(f"📁 Created {len(created_projects)} test projects")
        
        # Update .env file
        env_content = f"""# Redmine MCP test environment configuration
REDMINE_DOMAIN=http://localhost:3000
REDMINE_API_KEY={api_key}
REDMINE_TIMEOUT=30
DEBUG_MODE=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file updated")
        print("\n🚀 You can now test MCP functionality!")
        print("   Run: uv run python test_claude_integration.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
