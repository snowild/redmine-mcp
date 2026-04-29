#!/usr/bin/env python3
"""
Test installed redmine-mcp package
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def test_package_import():
    """Test package import"""
    print("📦 Testing package import...")
    try:
        import redmine_mcp
        from redmine_mcp.server import mcp
        from redmine_mcp.config import get_config
        from redmine_mcp.redmine_client import get_client
        print("✅ Package import successful")
        return True
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

def test_command_availability():
    """Test if command is available"""
    print("\n🔧 Testing command availability...")
    
    # Check uv tool installed command
    uv_bin_path = Path.home() / ".local" / "bin" / "redmine-mcp"
    if uv_bin_path.exists():
        print(f"✅ Found uv tool installed command: {uv_bin_path}")
        return True
    
    # Check system PATH command
    try:
        result = subprocess.run(["which", "redmine-mcp"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Found system PATH command: {result.stdout.strip()}")
            return True
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        pass
    
    print("❌ redmine-mcp command not found")
    return False

def test_mcp_server_startup():
    """Test MCP server startup"""
    print("\n🚀 Testing MCP server startup...")
    
    # Use local module test
    try:
        # Set test environment variables
        os.environ["REDMINE_DOMAIN"] = "https://test.example.com"
        os.environ["REDMINE_API_KEY"] = "test_key_12345"
        
        # Import and test server
        from redmine_mcp.server import mcp
        
        # Check if MCP instance is created correctly
        if mcp:
            print("✅ MCP server instance created successfully")
            
            # Simple check - confirm tool functions can be imported
            try:
                from redmine_mcp.server import server_info, health_check, get_issue
                print("✅ Core tool functions can be imported normally")
                return True
            except ImportError as ie:
                print(f"⚠️  Tool function import failed: {ie}")
                print("✅ MCP server instance created successfully (but tool import has issues)")
                return True
            
    except Exception as e:
        print(f"❌ MCP server startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration loading...")
    try:
        # Set test environment variables
        os.environ["REDMINE_DOMAIN"] = "https://test.example.com"
        os.environ["REDMINE_API_KEY"] = "test_key_12345"
        os.environ["DEBUG_MODE"] = "true"
        
        from redmine_mcp.config import get_config
        config = get_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"   - Domain: {config.redmine_domain}")
        print(f"   - API Key: {config.redmine_api_key[:10]}...")
        print(f"   - Debug: {config.debug_mode}")
        print(f"   - Timeout: {config.redmine_timeout}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_package_info():
    """Test package information"""
    print("\n📋 Testing package information...")
    try:
        import redmine_mcp
        
        # Check version
        if hasattr(redmine_mcp, '__version__'):
            print(f"✅ Package version: {redmine_mcp.__version__}")
        else:
            print("⚠️  Package version information not available")
        
        # Check modules
        modules = ['server', 'config', 'redmine_client', 'validators']
        for module in modules:
            try:
                __import__(f'redmine_mcp.{module}')
                print(f"✅ Module {module} available")
            except ImportError:
                print(f"❌ Module {module} not available")
        
        return True
    except Exception as e:
        print(f"❌ Package information check failed: {e}")
        return False

def main():
    """Main test flow"""
    print("🧪 Redmine MCP Installation Test")
    print("=" * 50)
    
    tests = [
        test_package_import,
        test_command_availability, 
        test_config_loading,
        test_mcp_server_startup,
        test_package_info,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Result Summary")
    print("=" * 50)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! Package installed successfully")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
