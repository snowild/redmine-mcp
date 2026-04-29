#!/usr/bin/env python3
"""
Test newly implemented MCP tools
Verify functionality by directly calling MCP tool functions
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from redmine_mcp.server import (
    search_users, list_users, get_user, refresh_cache,
    get_priorities, get_issue_statuses, get_trackers
)


def test_user_mcp_tools():
    """Test user-related MCP tools"""
    print("🔍 Test user MCP tools...")
    print("-" * 40)
    
    try:
        # Test search users
        print("1️⃣ Test search_users...")
        result = search_users("admin", 5)
        print(f"Search result:\n{result}\n")
        
        # Test list users
        print("2️⃣ Test list_users...")
        result = list_users(10, "active")
        print(f"User list:\n{result}\n")
        
        # Test get user details (assuming user ID 1 exists)
        print("3️⃣ Test get_user...")
        result = get_user(1)
        print(f"User details:\n{result}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ User MCP tool test failed: {e}")
        return False


def test_cache_mcp_tool():
    """Test cache MCP tool"""
    print("💾 Test cache MCP tool...")
    print("-" * 40)
    
    try:
        print("🔄 Test refresh_cache...")
        result = refresh_cache()
        print(f"Cache refresh result:\n{result}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache MCP tool test failed: {e}")
        return False


def test_enum_mcp_tools():
    """Test enumeration MCP tools (verify normal operation)"""
    print("📋 Test enumeration MCP tools...")
    print("-" * 40)
    
    try:
        print("1️⃣ Test get_priorities...")
        result = get_priorities()
        print(f"Priority list:\n{result}\n")
        
        print("2️⃣ Test get_issue_statuses...")
        result = get_issue_statuses()
        print(f"Status list:\n{result}\n")
        
        print("3️⃣ Test get_trackers...")
        result = get_trackers()
        print(f"Tracker list:\n{result}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Enumeration MCP tool test failed: {e}")
        return False


def test_helper_functions_integration():
    """Test helper function integration with actual data"""
    print("🔧 Test helper function integration...")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        
        client = get_client()
        
        # Test priority lookup
        print("1️⃣ Test priority name lookup...")
        priorities = client.get_available_priorities()
        if priorities:
            first_priority = list(priorities.keys())[0]
            priority_id = client.find_priority_id_by_name(first_priority)
            print(f"  Priority '{first_priority}' → ID: {priority_id}")
            assert priority_id == priorities[first_priority]
            print("  ✅ Priority lookup correct")
        
        # Test status lookup
        print("2️⃣ Test status name lookup...")
        statuses = client.get_available_statuses()
        if statuses:
            first_status = list(statuses.keys())[0]
            status_id = client.find_status_id_by_name(first_status)
            print(f"  Status '{first_status}' → ID: {status_id}")
            assert status_id == statuses[first_status]
            print("  ✅ Status lookup correct")
        
        # Test tracker lookup
        print("3️⃣ Test tracker name lookup...")
        trackers = client.get_available_trackers()
        if trackers:
            first_tracker = list(trackers.keys())[0]
            tracker_id = client.find_tracker_id_by_name(first_tracker)
            print(f"  Tracker '{first_tracker}' → ID: {tracker_id}")
            assert tracker_id == trackers[first_tracker]
            print("  ✅ Tracker lookup correct")
        
        # Test user lookup
        print("4️⃣ Test user name lookup...")
        users = client.get_available_users()
        if users['by_name']:
            first_user = list(users['by_name'].keys())[0]
            user_id = client.find_user_id_by_name(first_user)
            print(f"  User '{first_user}' → ID: {user_id}")
            assert user_id == users['by_name'][first_user]
            print("  ✅ User name lookup correct")
        
        if users['by_login']:
            first_login = list(users['by_login'].keys())[0]
            user_id = client.find_user_id_by_login(first_login)
            print(f"  Login '{first_login}' → ID: {user_id}")
            assert user_id == users['by_login'][first_login]
            print("  ✅ User login lookup correct")
            
            # Test smart lookup
            smart_id = client.find_user_id(first_login)
            assert smart_id == user_id
            print("  ✅ Smart user lookup correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Helper function integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_file_structure():
    """Test cache file structure"""
    print("📁 Test cache file structure...")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        import json
        
        client = get_client()
        
        # Ensure cache exists
        client.refresh_cache()
        
        # Check cache file
        cache_file = client._cache_file
        print(f"Cache file location: {cache_file}")
        
        if cache_file.exists():
            print("✅ Cache file exists")
            
            # Read and check structure
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            required_fields = ['cache_time', 'domain', 'priorities', 'statuses', 'trackers', 'users_by_name', 'users_by_login']
            
            for field in required_fields:
                if field in cache_data:
                    print(f"✅ Cache contains {field}: {len(cache_data[field]) if isinstance(cache_data[field], dict) else 'N/A'} items")
                else:
                    print(f"❌ Cache missing {field}")
                    return False
            
            # Check timestamp
            cache_time = cache_data['cache_time']
            if isinstance(cache_time, (int, float)) and cache_time > 0:
                from datetime import datetime
                cache_datetime = datetime.fromtimestamp(cache_time)
                print(f"✅ Cache time: {cache_datetime}")
            else:
                print("❌ Cache time format error")
                return False
            
            return True
        else:
            print("❌ Cache file does not exist")
            return False
            
    except Exception as e:
        print(f"❌ Cache file structure test failed: {e}")
        return False


def run_all_tests():
    """Run all MCP tool tests"""
    print("=" * 60)
    print("🚀 redmine-mcp new feature MCP tool test")
    print("=" * 60)
    
    tests = [
        ("User MCP tools", test_user_mcp_tools),
        ("Cache MCP tool", test_cache_mcp_tool),
        ("Enumeration MCP tools", test_enum_mcp_tools),
        ("Helper function integration", test_helper_functions_integration),
        ("Cache file structure", test_cache_file_structure),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running test: {test_name}")
        print("=" * 50)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
                
        except Exception as e:
            print(f"❌ {test_name} test exception: {e}")
            results.append((test_name, False))
    
    # Output summary
    print("\n" + "=" * 60)
    print("📊 Test result summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ Passed" if success else "❌ Failed"
        print(f"{test_name:<20} {status}")
    
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! New features are working normally!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed, please check related functions")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
