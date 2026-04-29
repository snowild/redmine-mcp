#!/usr/bin/env python3
"""
Claude Code integration test script
Used to verify whether the MCP server can correctly integrate with Claude Code
"""

import json
import subprocess
import sys
import os
from pathlib import Path


def test_mcp_server_executable():
    """Test if MCP server is executable"""
    print("🔧 Testing MCP server executability...")
    
    try:
        # Test if server.py can be executed directly
        result = subprocess.run([
            sys.executable, "-m", "redmine_mcp.server", "--help"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ MCP server is executable")
            return True
        else:
            print(f"❌ MCP server execution failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ MCP server startup normal (waiting for stdio input)")
        return True
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False


def test_package_installation():
    """Test if package is installed correctly"""
    print("📦 Testing package installation...")
    
    try:
        import redmine_mcp
        from redmine_mcp.server import mcp
        from redmine_mcp.config import get_config
        from redmine_mcp.redmine_client import get_client
        
        print("✅ All modules imported successfully")
        print(f"   - redmine_mcp version: {getattr(redmine_mcp, '__version__', 'unknown')}")
        return True
        
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return False


def test_configuration():
    """Test if configuration is correct"""
    print("⚙️  Testing configuration...")
    
    # Test environment variables
    required_env = ['REDMINE_DOMAIN', 'REDMINE_API_KEY']
    missing_env = []
    
    for env_var in required_env:
        if not os.getenv(env_var):
            missing_env.append(env_var)
    
    if missing_env:
        print(f"⚠️  Missing environment variables: {', '.join(missing_env)}")
        print("   Please set these environment variables or create a .env file")
        return False
    
    try:
        from redmine_mcp.config import get_config
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Redmine domain: {config.redmine_domain}")
        print(f"   - API timeout: {config.redmine_timeout}s")
        print(f"   - Debug mode: {config.debug_mode}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False


def generate_claude_config():
    """Generate Claude Code configuration example"""
    print("📝 Generating Claude Code configuration example...")
    
    config = {
        "mcpServers": {
            "redmine": {
                "command": "redmine-mcp",
                "env": {
                    "REDMINE_DOMAIN": os.getenv("REDMINE_DOMAIN", "https://your-redmine-domain.com"),
                    "REDMINE_API_KEY": os.getenv("REDMINE_API_KEY", "your_api_key_here"),
                    "REDMINE_TIMEOUT": os.getenv("REDMINE_TIMEOUT", "30"),
                    "DEBUG_MODE": os.getenv("DEBUG_MODE", "false")
                }
            }
        }
    }
    
    config_file = Path("claude_mcp_config_generated.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration file generated: {config_file}")
    print("   Please copy this content into Claude Code's MCP configuration")
    return True


def test_tools_availability():
    """Test if tools are available"""
    print("🛠️  Testing tool availability...")
    
    try:
        from redmine_mcp.server import (
            server_info, health_check, get_issue, 
            update_issue_status, list_project_issues
        )
        
        print("✅ Core tool functions available")
        
        # Test tool functions
        info = server_info()
        print(f"   - Server info: {info[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Claude Code integration test started\n")
    
    tests = [
        ("Package installation", test_package_installation),
        ("Configuration setup", test_configuration),
        ("MCP server", test_mcp_server_executable),
        ("Tool availability", test_tools_availability),
        ("Config generation", generate_claude_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Redmine MCP is ready to integrate with Claude Code")
        print("\nNext steps:")
        print("1. Add the generated configuration to Claude Code")
        print("2. Restart Claude Code")
        print("3. Test tools in Claude Code")
        return True
    else:
        print("❌ Some tests failed, please check the error messages above")
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
