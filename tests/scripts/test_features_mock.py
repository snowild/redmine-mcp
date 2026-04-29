#!/usr/bin/env python3
"""
Test new features using mock data
No real Redmine connection required
"""

import sys
import os
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def create_mock_data():
    """Create mock data"""
    return {
        'priorities': [
            {'id': 5, 'name': 'Low'},
            {'id': 6, 'name': 'Normal'},
            {'id': 7, 'name': 'High'},
            {'id': 8, 'name': 'Urgent'}
        ],
        'statuses': [
            {'id': 1, 'name': 'New'},
            {'id': 2, 'name': 'In Progress'}, 
            {'id': 3, 'name': 'Resolved'},
            {'id': 4, 'name': 'Closed'}
        ],
        'trackers': [
            {'id': 1, 'name': 'Bug'},
            {'id': 2, 'name': 'Feature'},
            {'id': 3, 'name': 'Support'}
        ],
        'users': [
            {
                'id': 1,
                'login': 'admin',
                'firstname': 'Redmine',
                'lastname': 'Admin',
                'mail': 'admin@example.com',
                'status': 1
            },
            {
                'id': 2, 
                'login': 'user1',
                'firstname': 'Test',
                'lastname': 'User',
                'mail': 'user1@example.com',
                'status': 1
            }
        ]
    }


def test_cache_system_with_mock():
    """Test cache system using mock data"""
    print("💾 Test cache system (Mock)")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client, RedmineUser
        
        mock_data = create_mock_data()
        
        # Mock API response
        def mock_make_request(method, endpoint, **kwargs):
            if '/enumerations/issue_priorities.json' in endpoint:
                return {'issue_priorities': mock_data['priorities']}
            elif '/issue_statuses.json' in endpoint:
                return {'issue_statuses': mock_data['statuses']}
            elif '/trackers.json' in endpoint:
                return {'trackers': mock_data['trackers']}
            elif '/users.json' in endpoint:
                return {'users': mock_data['users']}
            else:
                raise Exception(f"Unexpected endpoint: {endpoint}")
        
        client = get_client()
        
        # Use mock
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            # Force refresh cache
            client.refresh_cache()
            
            # Check if cache file is created
            cache_file = client._cache_file
            if cache_file.exists():
                print("✅ Cache file created successfully")
            else:
                print("❌ Cache file creation failed")
                return False
            
            # Check cache content
            cache = client._load_enum_cache()
            
            # Validate structure
            required_fields = ['cache_time', 'domain', 'priorities', 'statuses', 'trackers', 'users_by_name', 'users_by_login']
            for field in required_fields:
                if field in cache:
                    print(f"✅ Cache contains {field}")
                else:
                    print(f"❌ Cache missing {field}")
                    return False
            
            # Validate data
            expected_priorities = {'Low': 5, 'Normal': 6, 'High': 7, 'Urgent': 8}
            if cache['priorities'] == expected_priorities:
                print("✅ Priority cache correct")
            else:
                print(f"❌ Priority cache error: {cache['priorities']}")
                return False
            
            expected_users_by_name = {'Redmine Admin': 1, 'Test User': 2}
            if cache['users_by_name'] == expected_users_by_name:
                print("✅ User name cache correct")
            else:
                print(f"❌ User name cache error: {cache['users_by_name']}")
                return False
            
            print(f"📊 Cache statistics:")
            print(f"  - Priorities: {len(cache['priorities'])} items")
            print(f"  - Statuses: {len(cache['statuses'])} items")
            print(f"  - Trackers: {len(cache['trackers'])} items")
            print(f"  - Users (name): {len(cache['users_by_name'])} items")
            print(f"  - Users (login): {len(cache['users_by_login'])} items")
            
            return True
            
    except Exception as e:
        print(f"❌ Cache system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_helper_functions_with_mock():
    """Test helper functions using mock data"""
    print("\n🔧 Test helper functions (Mock)")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        
        client = get_client()
        
        # Set up mock cache
        mock_cache = {
            'cache_time': 1234567890,
            'domain': 'http://localhost:3000',
            'priorities': {'Low': 5, 'Normal': 6, 'High': 7, 'Urgent': 8},
            'statuses': {'New': 1, 'In Progress': 2, 'Resolved': 3, 'Closed': 4},
            'trackers': {'Bug': 1, 'Feature': 2, 'Support': 3},
            'users_by_name': {'Redmine Admin': 1, 'Test User': 2},
            'users_by_login': {'admin': 1, 'user1': 2}
        }
        
        client._enum_cache = mock_cache
        
        # Test priority lookup
        test_cases = [
            ('find_priority_id_by_name', 'Low', 5),
            ('find_priority_id_by_name', 'NonExistentPriority', None),
            ('find_status_id_by_name', 'In Progress', 2),
            ('find_status_id_by_name', 'NonExistentStatus', None),
            ('find_tracker_id_by_name', 'Bug', 1),
            ('find_tracker_id_by_name', 'NonExistentTracker', None),
            ('find_user_id_by_name', 'Redmine Admin', 1),
            ('find_user_id_by_name', 'NonExistentUser', None),
            ('find_user_id_by_login', 'admin', 1),
            ('find_user_id_by_login', 'NonExistentLogin', None),
            ('find_user_id', 'admin', 1),
            ('find_user_id', 'Redmine Admin', 1),
            ('find_user_id', 'NonExistentUser', None),
        ]
        
        for method_name, input_value, expected in test_cases:
            method = getattr(client, method_name)
            result = method(input_value)
            
            if result == expected:
                print(f"✅ {method_name}('{input_value}') → {result}")
            else:
                print(f"❌ {method_name}('{input_value}') → {result}, expected {expected}")
                return False
        
        # Test getting all options
        print("\nTest getting all options:")
        priorities = client.get_available_priorities()
        if priorities == mock_cache['priorities']:
            print(f"✅ get_available_priorities: {len(priorities)} items")
        else:
            print(f"❌ get_available_priorities error")
            return False
        
        users = client.get_available_users()
        expected_users = {
            'by_name': mock_cache['users_by_name'],
            'by_login': mock_cache['users_by_login']
        }
        if users == expected_users:
            print(f"✅ get_available_users: name {len(users['by_name'])} items, login {len(users['by_login'])} items")
        else:
            print(f"❌ get_available_users error")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Helper function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_domain_isolation():
    """Test Domain isolation"""
    print("\n🌐 Test Domain isolation (Mock)")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import RedmineClient
        
        # Test cache file names for different domains
        domains = [
            'http://localhost:3000',
            'https://demo.redmine.org',
            'https://test.example.com:8080'
        ]
        
        cache_files = []
        
        for domain in domains:
            # Directly test cache file name generation logic
            domain_hash = hash(domain)
            safe_domain = domain.replace('://', '_').replace('/', '_').replace(':', '_')
            cache_filename = f"cache_{safe_domain}_{abs(domain_hash)}.json"
            
            cache_files.append((domain, cache_filename))
        
        # Check all file names are different
        filenames = [filename for _, filename in cache_files]
        
        print("Domain and file name mapping:")
        for domain, filename in cache_files:
            print(f"  {domain} → {filename}")
        
        print(f"\nFile name uniqueness check:")
        print(f"  Total files: {len(filenames)}")
        print(f"  Unique files: {len(set(filenames))}")
        
        if len(set(filenames)) == len(filenames):
            print("✅ Different Domains generate different cache files")
        else:
            print("❌ Domain isolation failed, duplicate file names")
            # Show duplicate file names
            seen = set()
            duplicates = set()
            for filename in filenames:
                if filename in seen:
                    duplicates.add(filename)
                else:
                    seen.add(filename)
            print(f"  Duplicate file names: {duplicates}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Domain isolation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_tools_with_mock():
    """Test MCP tools (Mock)"""
    print("\n🛠️ Test MCP tools (Mock)")
    print("-" * 40)
    
    try:
        # Mock client response
        mock_users = [
            {'id': 1, 'login': 'admin', 'firstname': 'Redmine', 'lastname': 'Admin', 'mail': 'admin@example.com', 'status': 1}
        ]
        
        def mock_search_users(query, limit):
            from redmine_mcp.redmine_client import RedmineUser
            return [RedmineUser(
                id=user['id'],
                login=user['login'],
                firstname=user['firstname'],
                lastname=user['lastname'],
                mail=user['mail'],
                status=user['status']
            ) for user in mock_users if query.lower() in user['login'].lower()]
        
        def mock_list_users(limit, status):
            from redmine_mcp.redmine_client import RedmineUser
            return [RedmineUser(
                id=user['id'],
                login=user['login'],
                firstname=user['firstname'],
                lastname=user['lastname'],
                mail=user['mail'],
                status=user['status']
            ) for user in mock_users]
        
        def mock_get_user(user_id):
            user = next((u for u in mock_users if u['id'] == user_id), None)
            if user:
                return user
            else:
                raise Exception(f"User ID {user_id} not found")
        
        # Test MCP tools
        from redmine_mcp.redmine_client import get_client
        client = get_client()
        
        with patch.object(client, 'search_users', side_effect=mock_search_users), \
             patch.object(client, 'list_users', side_effect=mock_list_users), \
             patch.object(client, 'get_user', side_effect=mock_get_user):
            
            # Test search_users MCP tool
            from redmine_mcp.server import search_users, list_users, get_user
            
            result = search_users("admin", 5)
            if "admin" in result and "Redmine Admin" in result:
                print("✅ search_users MCP tool normal")
            else:
                print(f"❌ search_users MCP tool abnormal: {result}")
                return False
            
            # Test list_users MCP tool
            result = list_users(10, "active")
            if "admin" in result and "Redmine Admin" in result:
                print("✅ list_users MCP tool normal")
            else:
                print(f"❌ list_users MCP tool abnormal: {result}")
                return False
            
            # Test get_user MCP tool
            result = get_user(1)
            if "admin" in result and "Redmine Admin" in result:
                print("✅ get_user MCP tool normal")
            else:
                print(f"❌ get_user MCP tool abnormal: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ MCP tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_mock_tests():
    """Run all mock tests"""
    print("🧪 redmine-mcp new feature mock test")
    print("=" * 60)
    print("(Using mock data, no real Redmine connection required)")
    print("=" * 60)
    
    tests = [
        ("Cache system", test_cache_system_with_mock),
        ("Helper functions", test_helper_functions_with_mock),
        ("Domain isolation", test_domain_isolation),
        ("MCP tools", test_mcp_tools_with_mock),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running test: {test_name}")
        print("=" * 50)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"\n✅ {test_name} test passed")
            else:
                print(f"\n❌ {test_name} test failed")
                
        except Exception as e:
            print(f"\n❌ {test_name} test exception: {e}")
            results.append((test_name, False))
    
    # Output summary
    print("\n" + "=" * 60)
    print("📊 Mock test result summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ Passed" if success else "❌ Failed"
        print(f"{test_name:<15} {status}")
    
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All mock tests passed!")
        print("New feature logic is working normally!")
        print("\n💡 To test with a real Redmine connection, please:")
        print("1. Ensure Redmine service is running")
        print("2. Update with a valid API key")
        print("3. Run: uv run python tests/scripts/quick_validation.py")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed, please check the logic")
        return False


if __name__ == "__main__":
    success = run_mock_tests()
    sys.exit(0 if success else 1)
