#!/usr/bin/env python3
"""
Quick validation simplified test script for new features
Mainly tests if core functions are working normally
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def quick_test():
    """Quick test core functions"""
    print("🚀 Quick validation of redmine-mcp new features")
    print("=" * 50)
    
    try:
        # Test basic connection
        print("1️⃣ Testing basic connection...")
        from redmine_mcp.redmine_client import get_client
        client = get_client()
        
        if client.test_connection():
            print("✅ Redmine connection normal")
        else:
            print("❌ Redmine connection failed")
            return False
        
        # Test cache system
        print("\n2️⃣ Testing cache system...")
        cache_dir = client.cache_dir
        cache_file = client._cache_file
        
        print(f"  Cache directory: {cache_dir}")
        print(f"  Cache file: {cache_file.name}")
        
        if cache_dir.exists():
            print("✅ Cache directory exists")
        else:
            print("❌ Cache directory does not exist")
            return False
        
        # Refresh cache
        print("\n3️⃣ Testing cache refresh...")
        client.refresh_cache()
        
        if cache_file.exists():
            print("✅ Cache file created successfully")
        else:
            print("❌ Cache file creation failed")
            return False
        
        # Test helper functions
        print("\n4️⃣ Testing helper functions...")
        
        # Test priority query
        priorities = client.get_available_priorities()
        if priorities:
            priority_name = list(priorities.keys())[0]
            priority_id = client.find_priority_id_by_name(priority_name)
            if priority_id:
                print(f"✅ Priority query normal: '{priority_name}' → {priority_id}")
            else:
                print("❌ Priority query failed")
                return False
        else:
            print("⚠️ No priority data available for testing")
        
        # Test status query
        statuses = client.get_available_statuses()
        if statuses:
            status_name = list(statuses.keys())[0]
            status_id = client.find_status_id_by_name(status_name)
            if status_id:
                print(f"✅ Status query normal: '{status_name}' → {status_id}")
            else:
                print("❌ Status query failed")
                return False
        else:
            print("⚠️ No status data available for testing")
        
        # Test user query
        print("\n5️⃣ Testing user query...")
        try:
            users = client.list_users(limit=5)
            if users:
                print(f"✅ User query normal: found {len(users)} users")
                
                # Test user cache
                cache = client._load_enum_cache()
                users_by_name = cache.get('users_by_name', {})
                users_by_login = cache.get('users_by_login', {})
                
                if users_by_name or users_by_login:
                    print(f"✅ User cache normal: name {len(users_by_name)} items, login {len(users_by_login)} items")
                else:
                    print("⚠️ User cache is empty")
            else:
                print("⚠️ No user data available for testing")
        except Exception as e:
            print(f"⚠️ User query skipped (may be insufficient permissions): {e}")
        
        # Test MCP tools
        print("\n6️⃣ Testing MCP tools...")
        try:
            from redmine_mcp.server import get_priorities, refresh_cache
            
            # Test get_priorities
            result = get_priorities()
            if "priorities" in result.lower():
                print("✅ get_priorities MCP tool normal")
            else:
                print("❌ get_priorities MCP tool abnormal")
                return False
            
            # Test refresh_cache
            result = refresh_cache()
            if "success" in result.lower():
                print("✅ refresh_cache MCP tool normal")
            else:
                print("❌ refresh_cache MCP tool abnormal")
                return False
                
        except Exception as e:
            print(f"❌ MCP tool test failed: {e}")
            return False
        
        # Output cache statistics
        print("\n📊 Cache statistics:")
        cache = client._load_enum_cache()
        print(f"  - Domain: {cache.get('domain', 'N/A')}")
        print(f"  - Priorities: {len(cache.get('priorities', {}))} items")
        print(f"  - Statuses: {len(cache.get('statuses', {}))} items")
        print(f"  - Trackers: {len(cache.get('trackers', {}))} items")
        print(f"  - Users (name): {len(cache.get('users_by_name', {}))} items")
        print(f"  - Users (login): {len(cache.get('users_by_login', {}))} items")
        
        print("\n🎉 All core functionality validations passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Validation process error: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_usage_examples():
    """Display usage examples"""
    print("\n" + "=" * 50)
    print("💡 Usage Examples")
    print("=" * 50)
    
    examples = [
        "# Query ID by name",
        "from redmine_mcp.redmine_client import get_client",
        "client = get_client()",
        "",
        "# Query priority ID",
        'priority_id = client.find_priority_id_by_name("Low")',
        "",
        "# Query status ID", 
        'status_id = client.find_status_id_by_name("In Progress")',
        "",
        "# Query user ID",
        'user_id = client.find_user_id("Redmine Admin")',
        "",
        "# Get all available options",
        "priorities = client.get_available_priorities()",
        "users = client.get_available_users()",
        "",
        "# Manually refresh cache",
        "client.refresh_cache()",
    ]
    
    for example in examples:
        print(example)


if __name__ == "__main__":
    success = quick_test()
    
    if success:
        display_usage_examples()
    
    print(f"\n{'='*50}")
    print(f"Validation result: {'✅ Success' if success else '❌ Failure'}")
    print(f"{'='*50}")
    
    sys.exit(0 if success else 1)
