#!/usr/bin/env python3
"""
Script to enable Redmine REST API
"""

import requests
import re
import time

def enable_rest_api():
    """Enable REST API via web interface"""
    session = requests.Session()
    url = "http://localhost:3000"
    
    try:
        print("🔐 Logging in to admin account...")
        
        # Get login page and CSRF token
        response = session.get(f"{url}/login")
        csrf_match = re.search(r'name="authenticity_token" value="([^"]+)"', response.text)
        if not csrf_match:
            print("❌ CSRF token not found")
            return False
        
        csrf_token = csrf_match.group(1)
        
        # Login
        login_data = {
            'username': 'admin',
            'password': 'admin',
            'authenticity_token': csrf_token
        }
        
        response = session.post(f"{url}/login", data=login_data, allow_redirects=False)
        if response.status_code not in [302, 200]:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        print("✅ Login successful")
        
        # Go to settings page
        print("⚙️  Accessing system settings...")
        response = session.get(f"{url}/settings")
        if response.status_code != 200:
            print(f"❌ Cannot access settings page: {response.status_code}")
            return False
        
        # Check current REST API status
        if 'rest_api_enabled' in response.text:
            print("📡 Found REST API settings")
        else:
            print("⚠️  REST API settings option not found")
            
        # Get CSRF token from settings page
        csrf_match = re.search(r'name="authenticity_token" value="([^"]+)"', response.text)
        if not csrf_match:
            print("❌ CSRF token not found on settings page")
            return False
        
        csrf_token = csrf_match.group(1)
        
        # Prepare data to enable REST API
        print("🔧 Enabling REST API...")
        settings_data = {
            'authenticity_token': csrf_token,
            'settings[rest_api_enabled]': '1',  # Enable REST API
            'settings[jsonp_enabled]': '0',     # Keep JSONP disabled
            'commit': 'Save'
        }
        
        response = session.post(f"{url}/settings", data=settings_data)
        
        if response.status_code == 200:
            print("✅ REST API settings updated")
            
            # Verify settings are effective
            time.sleep(1)
            test_response = session.get(f"{url}/issues.json")
            print(f"🧪 API test response: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print("🎉 REST API enabled successfully!")
                return True
            else:
                print("⚠️  REST API may still not be working properly")
        else:
            print(f"❌ Settings update failed: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return False

def main():
    print("🚀 Redmine REST API Enabler")
    print("=" * 40)
    
    if enable_rest_api():
        print("\n🎯 Next steps:")
        print("1. Run: uv run python configure_redmine.py")
        print("2. Or manually obtain API key and run:")
        print("   python manual_api_setup.py <API_KEY>")
        return True
    else:
        print("\n❌ REST API enablement failed")
        print("Please enable manually:")
        print("1. Open http://localhost:3000")
        print("2. Log in with admin/admin")
        print("3. Go to Administration > Settings > API")
        print("4. Check 'Enable REST web service'")
        print("5. Click Save")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
