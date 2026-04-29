#!/usr/bin/env python3
"""
Check redmine-mcp configuration and environment setup
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def check_configuration():
    """Check if configuration is correct"""
    print("🔧 Checking redmine-mcp configuration")
    print("=" * 50)
    
    # Check environment variables
    print("1️⃣ Checking environment variables...")
    
    required_vars = {
        'REDMINE_DOMAIN': 'Required - Redmine server URL',
        'REDMINE_API_KEY': 'Required - Redmine API key'
    }
    
    optional_vars = {
        'REDMINE_MCP_LOG_LEVEL': 'Optional - Log level',
        'REDMINE_MCP_TIMEOUT': 'Optional - Request timeout',
        'LOG_LEVEL': 'Fallback - Log level (fallback)',
        'REDMINE_TIMEOUT': 'Fallback - Request timeout (fallback)'
    }
    
    missing_required = []
    
    print("\nRequired environment variables:")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # Hide API key
            display_value = value if var != 'REDMINE_API_KEY' else f"{value[:8]}...{value[-4:]}"
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set ({desc})")
            missing_required.append(var)
    
    print("\nOptional environment variables:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚪ {var}: Not set ({desc})")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("\nSetup method:")
        print("export REDMINE_DOMAIN='https://your-redmine-domain.com'")
        print("export REDMINE_API_KEY='your_api_key_here'")
        return False
    
    # Try loading configuration
    print("\n2️⃣ Testing configuration loading...")
    try:
        from redmine_mcp.config import get_config
        config = get_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"  - Domain: {config.redmine_domain}")
        print(f"  - API Key: {config.redmine_api_key[:8]}...{config.redmine_api_key[-4:]}")
        print(f"  - Timeout: {config.redmine_timeout}s")
        print(f"  - Log Level: {config.log_level}")
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    # Test client initialization
    print("\n3️⃣ Testing client initialization...")
    try:
        from redmine_mcp.redmine_client import get_client
        client = get_client()
        
        print(f"✅ Client initialization successful")
        print(f"  - Cache directory: {client.cache_dir}")
        print(f"  - Cache file: {client._cache_file.name}")
        
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False
    
    # Test network connection (does not require valid API)
    print("\n4️⃣ Testing network connection...")
    try:
        import requests
        from urllib.parse import urlparse
        
        parsed = urlparse(config.redmine_domain)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        response = requests.get(base_url, timeout=10)
        print(f"✅ Network connection normal (HTTP {response.status_code})")
        
    except Exception as e:
        print(f"⚠️ Network connection test failed: {e}")
        print("    This may be normal if Redmine requires special authentication")
    
    print("\n✅ Basic configuration check completed")
    return True


def test_offline_features():
    """Test features that do not require network connection"""
    print("\n🔧 Testing offline features")
    print("=" * 50)
    
    try:
        from redmine_mcp.redmine_client import get_client
        
        client = get_client()
        
        # Test cache directory creation
        print("1️⃣ Testing cache directory...")
        cache_dir = client.cache_dir
        
        if cache_dir.exists():
            print(f"✅ Cache directory exists: {cache_dir}")
        else:
            print(f"⚠️ Cache directory does not exist, trying to create...")
            cache_dir.mkdir(parents=True, exist_ok=True)
            if cache_dir.exists():
                print(f"✅ Cache directory created successfully: {cache_dir}")
            else:
                print(f"❌ Cache directory creation failed")
                return False
        
        # Test cache file naming
        print("\n2️⃣ Testing cache file naming...")
        cache_file = client._cache_file
        print(f"✅ Cache file name: {cache_file.name}")
        
        # Check if file name contains domain information
        from redmine_mcp.config import get_config
        config = get_config()
        domain_part = config.redmine_domain.replace('://', '_').replace('/', '_').replace(':', '_')
        
        if domain_part in cache_file.name:
            print(f"✅ File name contains domain information")
        else:
            print(f"⚠️ File name may have issues")
        
        # Test empty cache structure
        print("\n3️⃣ Testing empty cache structure...")
        empty_cache = {
            'cache_time': 0,
            'domain': config.redmine_domain,
            'priorities': {},
            'statuses': {},
            'trackers': {},
            'users_by_name': {},
            'users_by_login': {}
        }
        
        import json
        test_content = json.dumps(empty_cache, ensure_ascii=False, indent=2)
        print(f"✅ Cache structure test passed")
        
        # Test helper functions (with empty data)
        print("\n4️⃣ Testing helper functions (empty data)...")
        
        # Set empty cache
        client._enum_cache = empty_cache
        
        result = client.find_priority_id_by_name("NonExistentPriority")
        if result is None:
            print("✅ find_priority_id_by_name correctly returns None")
        else:
            print("❌ find_priority_id_by_name should return None")
            return False
        
        result = client.find_user_id("Non-existent user")
        if result is None:
            print("✅ find_user_id correctly returns None")
        else:
            print("❌ find_user_id should return None")
            return False
        
        print("\n✅ Offline feature test completed")
        return True
        
    except Exception as e:
        print(f"❌ Offline feature test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test flow"""
    print("🧪 redmine-mcp configuration and offline feature test")
    print("=" * 60)
    
    # Configuration check
    config_ok = check_configuration()
    
    # Offline feature test
    offline_ok = test_offline_features()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    print(f"Configuration check: {'✅ Passed' if config_ok else '❌ Failed'}")
    print(f"Offline features: {'✅ Passed' if offline_ok else '❌ Failed'}")
    
    if config_ok and offline_ok:
        print("\n🎉 Basic functions normal! Can proceed with further testing")
        print("\n💡 To test full functionality, please ensure:")
        print("1. REDMINE_DOMAIN points to an accessible Redmine server")
        print("2. REDMINE_API_KEY is a valid API key")
        print("3. Network connection is normal")
        print("\nThen run: uv run python tests/scripts/quick_validation.py")
        return True
    else:
        print("\n❌ Basic functions have issues, please check configuration")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
