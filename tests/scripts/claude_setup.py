#!/usr/bin/env python3
"""
Test Claude Code MCP configuration
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

def test_mcp_config_generation():
    """Test MCP configuration file generation"""
    print("📋 Testing MCP configuration file generation...")
    
    try:
        # Create test configuration
        config = {
            "mcpServers": {
                "redmine": {
                    "command": "redmine-mcp",
                    "env": {
                        "REDMINE_DOMAIN": "https://demo.redmine.org",
                        "REDMINE_API_KEY": "test_api_key_12345",
                        "REDMINE_TIMEOUT": "30",
                        "DEBUG_MODE": "false"
                    }
                }
            }
        }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            temp_path = f.name
        
        # Validate JSON format
        with open(temp_path, 'r') as f:
            loaded_config = json.load(f)
        
        print("✅ MCP configuration file format correct")
        print(f"   Configuration contains {len(loaded_config['mcpServers'])} MCP servers")
        print(f"   Redmine server configuration: {loaded_config['mcpServers']['redmine']['command']}")
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"❌ MCP configuration file generation failed: {e}")
        return False

def test_command_execution():
    """Test command execution"""
    print("\n🔧 Testing command execution...")
    
    try:
        # Check if redmine-mcp command exists
        uv_bin_path = Path.home() / ".local" / "bin" / "redmine-mcp"
        
        if not uv_bin_path.exists():
            print("❌ redmine-mcp command does not exist")
            return False
        
        print(f"✅ Found command: {uv_bin_path}")
        
        # Test command executability (don't actually execute, as it will wait for stdio)
        if os.access(uv_bin_path, os.X_OK):
            print("✅ Command has execution permission")
            return True
        else:
            print("❌ Command does not have execution permission")
            return False
            
    except Exception as e:
        print(f"❌ Command execution test failed: {e}")
        return False

def generate_setup_instructions():
    """Generate setup instructions"""
    print("\n📖 Generating Claude Code setup instructions...")
    
    try:
        # Find installation path
        uv_bin_path = Path.home() / ".local" / "bin" / "redmine-mcp"
        
        instructions = f"""
Claude Code MCP Setup Instructions
========================

1. Verify installation
   Command location: {uv_bin_path}
   Status: {'✅ Installed' if uv_bin_path.exists() else '❌ Not installed'}

2. Manually add to Claude Code
   Run the following command to add Redmine MCP to Claude Code:

   ```bash
   claude mcp add redmine "{uv_bin_path}" \\
     -e REDMINE_DOMAIN="https://your-redmine-domain.com" \\
     -e REDMINE_API_KEY="your_api_key_here"
   ```

3. Or manually edit MCP configuration file
   
   Configuration file location:
   - macOS/Linux: ~/.config/claude-code/mcp_servers.json
   - Windows: %APPDATA%\\claude-code\\mcp_servers.json
   
   Configuration content:
   ```json
   {{
     "mcpServers": {{
       "redmine": {{
         "command": "{uv_bin_path}",
         "env": {{
           "REDMINE_DOMAIN": "https://your-redmine-domain.com",
           "REDMINE_API_KEY": "your_api_key_here",
           "REDMINE_TIMEOUT": "30",
           "DEBUG_MODE": "false"
         }}
       }}
     }}
   }}
   ```

4. Restart Claude Code
   After setup is complete, restart Claude Code to load the MCP server.

5. Verify setup
   Enter in Claude Code: "Please run a health check"
   If you see a Redmine connection status response, the setup is successful.
"""
        
        print(instructions)
        
        # Write to file
        setup_file = Path("CLAUDE_SETUP.md")
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"✅ Setup instructions saved to: {setup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Setup instructions generation failed: {e}")
        return False

def main():
    """Main test flow"""
    print("🔗 Claude Code MCP Setup Test")
    print("=" * 50)
    
    tests = [
        test_mcp_config_generation,
        test_command_execution,
        generate_setup_instructions,
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
        print("\n🎉 Claude Code setup test passed!")
        print("💡 Please refer to CLAUDE_SETUP.md to complete Claude Code integration setup")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
