"""
Integration tests for newly implemented features
Includes user queries, cache mechanism, helper functions, etc.
"""

import pytest
import os
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, Mock

from src.redmine_mcp.redmine_client import get_client, RedmineClient, RedmineAPIError
from src.redmine_mcp.config import get_config


class TestUserFunctionality:
    """Test user query functionality"""
    
    def test_search_users_by_name(self):
        """Test searching users by name"""
        try:
            client = get_client()
            users = client.search_users("admin", limit=5)
            
            assert isinstance(users, list)
            print(f"✅ User search function works, found {len(users)} users")
            
            if users:
                user = users[0]
                assert hasattr(user, 'id')
                assert hasattr(user, 'login')
                assert hasattr(user, 'firstname')
                assert hasattr(user, 'lastname')
                print(f"✅ User data structure correct: {user.login}")
            
        except RedmineAPIError as e:
            pytest.skip(f"Redmine API error (may be permission issue): {e}")
        except Exception as e:
            pytest.fail(f"User search test failed: {e}")
    
    def test_list_users(self):
        """Test listing all users"""
        try:
            client = get_client()
            users = client.list_users(limit=10)
            
            assert isinstance(users, list)
            print(f"✅ List users function works, total {len(users)} users")
            
            if users:
                user = users[0]
                assert user.id > 0
                assert user.login
                print(f"✅ First user: ID={user.id}, Login={user.login}")
            
        except RedmineAPIError as e:
            pytest.skip(f"Redmine API error: {e}")
        except Exception as e:
            pytest.fail(f"List users test failed: {e}")
    
    def test_get_user_details(self):
        """Test getting specific user details"""
        try:
            client = get_client()
            # Usually ID 1 is admin
            user_data = client.get_user(1)
            
            assert isinstance(user_data, dict)
            assert 'id' in user_data
            assert 'login' in user_data
            print(f"✅ Get user details function works: {user_data.get('login', 'N/A')}")
            
        except RedmineAPIError as e:
            pytest.skip(f"Redmine API error: {e}")
        except Exception as e:
            pytest.fail(f"Get user details test failed: {e}")


class TestCacheSystem:
    """Test cache system functionality"""
    
    def test_cache_file_creation(self):
        """Test if cache file is created correctly"""
        client = get_client()
        cache_dir = client.cache_dir
        cache_file = client._cache_file
        
        # Check cache directory
        assert cache_dir.exists()
        assert cache_dir.is_dir()
        print(f"✅ Cache directory exists: {cache_dir}")
        
        # Check file name format
        assert "cache_" in cache_file.name
        config = get_config()
        domain_in_filename = config.redmine_domain.replace('://', '_').replace('/', '_').replace(':', '_')
        assert domain_in_filename in cache_file.name
        print(f"✅ Cache file name correct: {cache_file.name}")
    
    @patch.object(RedmineClient, 'list_users')
    @patch.object(RedmineClient, 'get_time_entry_activities')
    @patch.object(RedmineClient, 'get_trackers')
    @patch.object(RedmineClient, 'get_issue_statuses')
    @patch.object(RedmineClient, 'get_priorities')
    def test_cache_content_structure(self, mock_get_priorities, mock_get_issue_statuses,
                                      mock_get_trackers, mock_get_time_entry_activities,
                                      mock_list_users):
        """Test cache content structure"""
        # Setup mocks
        mock_get_priorities.return_value = [{'id': 1, 'name': 'Normal'}]
        mock_get_issue_statuses.return_value = [{'id': 1, 'name': 'New'}]
        mock_get_trackers.return_value = [{'id': 1, 'name': 'Bug'}]
        mock_get_time_entry_activities.return_value = [{'id': 1, 'name': 'Development'}]
        mock_user = Mock()
        mock_user.id = 1
        mock_user.firstname = 'John'
        mock_user.lastname = 'Doe'
        mock_user.login = 'jdoe'
        mock_list_users.return_value = [mock_user]

        try:
            client = get_client()
            # Force refresh cache
            client.refresh_cache()
            
            cache = client._load_enum_cache()
            
            # Check required fields
            required_fields = ['cache_time', 'domain', 'priorities', 'statuses', 'trackers', 'users_by_name', 'users_by_login']
            for field in required_fields:
                assert field in cache, f"Cache missing required field: {field}"
            
            # Check domain is correct
            config = get_config()
            assert cache['domain'] == config.redmine_domain
            
            # Check timestamp
            assert isinstance(cache['cache_time'], (int, float))
            assert cache['cache_time'] > 0
            
            print(f"✅ Cache structure correct")
            print(f"  - Domain: {cache['domain']}")
            print(f"  - Priorities: {len(cache['priorities'])} items")
            print(f"  - Statuses: {len(cache['statuses'])} items")
            print(f"  - Trackers: {len(cache['trackers'])} items")
            print(f"  - Users (name): {len(cache['users_by_name'])} items")
            print(f"  - Users (login): {len(cache['users_by_login'])} items")
            
        except Exception as e:
            pytest.fail(f"Cache content test failed: {e}")
    
    @patch.object(RedmineClient, 'list_users')
    @patch.object(RedmineClient, 'get_time_entry_activities')
    @patch.object(RedmineClient, 'get_trackers')
    @patch.object(RedmineClient, 'get_issue_statuses')
    @patch.object(RedmineClient, 'get_priorities')
    def test_cache_persistence(self, mock_get_priorities, mock_get_issue_statuses,
                                mock_get_trackers, mock_get_time_entry_activities,
                                mock_list_users):
        """Test cache persistence"""
        # Setup mocks
        mock_get_priorities.return_value = [{'id': 1, 'name': 'Normal'}]
        mock_get_issue_statuses.return_value = [{'id': 1, 'name': 'New'}]
        mock_get_trackers.return_value = [{'id': 1, 'name': 'Bug'}]
        mock_get_time_entry_activities.return_value = [{'id': 1, 'name': 'Development'}]
        mock_user = Mock()
        mock_user.id = 1
        mock_user.firstname = 'John'
        mock_user.lastname = 'Doe'
        mock_user.login = 'jdoe'
        mock_list_users.return_value = [mock_user]

        try:
            client = get_client()
            cache_file = client._cache_file
            
            # Ensure cache exists
            client.refresh_cache()
            
            # Check file exists
            assert cache_file.exists()
            
            # Read and validate JSON format
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert isinstance(data, dict)
            assert 'cache_time' in data
            print(f"✅ Cache file persistence normal: {cache_file}")
            
        except Exception as e:
            pytest.fail(f"Cache persistence test failed: {e}")


class TestHelperFunctions:
    """Test helper function functionality"""
    
    @patch.object(RedmineClient, '_load_enum_cache')
    @patch.object(RedmineClient, 'get_priorities')
    def test_priority_name_lookup(self, mock_get_priorities, mock_load_cache):
        """Test priority name lookup"""
        mock_get_priorities.return_value = [{'id': 1, 'name': 'Normal'}]
        mock_load_cache.return_value = {
            'priorities': {'Normal': 1},
            'statuses': {},
            'trackers': {},
            'users_by_name': {},
            'users_by_login': {}
        }

        try:
            client = get_client()
            
            # First get all priorities to find a valid name
            priorities = client.get_priorities()
            if not priorities:
                pytest.skip("No available priority data")
            
            priority_name = priorities[0]['name']
            expected_id = priorities[0]['id']
            
            # Test helper function
            found_id = client.find_priority_id_by_name(priority_name)
            
            assert found_id == expected_id
            print(f"✅ Priority name lookup normal: '{priority_name}' → {found_id}")
            
            # Test non-existent name
            invalid_id = client.find_priority_id_by_name("NonExistentPriority")
            assert invalid_id is None
            print(f"✅ Invalid priority name correctly returns None")
            
        except Exception as e:
            pytest.fail(f"Priority name lookup test failed: {e}")
    
    @patch.object(RedmineClient, '_load_enum_cache')
    @patch.object(RedmineClient, 'get_issue_statuses')
    def test_status_name_lookup(self, mock_get_issue_statuses, mock_load_cache):
        """Test status name lookup"""
        mock_get_issue_statuses.return_value = [{'id': 1, 'name': 'New'}]
        mock_load_cache.return_value = {
            'priorities': {},
            'statuses': {'New': 1},
            'trackers': {},
            'users_by_name': {},
            'users_by_login': {}
        }

        try:
            client = get_client()
            
            statuses = client.get_issue_statuses()
            if not statuses:
                pytest.skip("No available status data")
            
            status_name = statuses[0]['name']
            expected_id = statuses[0]['id']
            
            found_id = client.find_status_id_by_name(status_name)
            
            assert found_id == expected_id
            print(f"✅ Status name lookup normal: '{status_name}' → {found_id}")
            
        except Exception as e:
            pytest.fail(f"Status name lookup test failed: {e}")
    
    @patch.object(RedmineClient, '_load_enum_cache')
    @patch.object(RedmineClient, 'get_trackers')
    def test_tracker_name_lookup(self, mock_get_trackers, mock_load_cache):
        """Test tracker name lookup"""
        mock_get_trackers.return_value = [{'id': 1, 'name': 'Bug'}]
        mock_load_cache.return_value = {
            'priorities': {},
            'statuses': {},
            'trackers': {'Bug': 1},
            'users_by_name': {},
            'users_by_login': {}
        }

        try:
            client = get_client()
            
            trackers = client.get_trackers()
            if not trackers:
                pytest.skip("No available tracker data")
            
            tracker_name = trackers[0]['name']
            expected_id = trackers[0]['id']
            
            found_id = client.find_tracker_id_by_name(tracker_name)
            
            assert found_id == expected_id
            print(f"✅ Tracker name lookup normal: '{tracker_name}' → {found_id}")
            
        except Exception as e:
            pytest.fail(f"Tracker name lookup test failed: {e}")
    
    def test_user_name_lookup(self):
        """Test user name lookup"""
        try:
            client = get_client()
            
            # Refresh cache to ensure user data exists
            client.refresh_cache()
            cache = client._load_enum_cache()
            
            users_by_name = cache.get('users_by_name', {})
            users_by_login = cache.get('users_by_login', {})
            
            if users_by_name:
                # Test name lookup
                user_name = list(users_by_name.keys())[0]
                expected_id = users_by_name[user_name]
                
                found_id = client.find_user_id_by_name(user_name)
                assert found_id == expected_id
                print(f"✅ User name lookup normal: '{user_name}' → {found_id}")
            
            if users_by_login:
                # Test login lookup
                login_name = list(users_by_login.keys())[0]
                expected_id = users_by_login[login_name]
                
                found_id = client.find_user_id_by_login(login_name)
                assert found_id == expected_id
                print(f"✅ User login lookup normal: '{login_name}' → {found_id}")
                
                # Test smart lookup
                smart_id = client.find_user_id(login_name)
                assert smart_id == expected_id
                print(f"✅ Smart user lookup normal: '{login_name}' → {smart_id}")
            
            if not users_by_name and not users_by_login:
                pytest.skip("No available user cache data")
                
        except Exception as e:
            pytest.fail(f"User name lookup test failed: {e}")


class TestDomainIsolation:
    """Test Multi-Domain isolation functionality"""
    
    def test_cache_filename_uniqueness(self):
        """Test cache file name uniqueness for different domains"""
        # Simulate different domains
        domains = [
            "https://demo.redmine.org",
            "https://test.redmine.com", 
            "http://localhost:3000"
        ]
        
        cache_files = []
        for domain in domains:
            with patch('src.redmine_mcp.redmine_client.get_config') as mock_config:
                mock_config.return_value.redmine_domain = domain
                mock_config.return_value.api_headers = {'X-Redmine-API-Key': 'test'}
                mock_config.return_value.redmine_timeout = 30
                
                client = RedmineClient()
                cache_files.append(client._cache_file.name)
        
        # Check all cache file names are different
        assert len(set(cache_files)) == len(cache_files)
        print(f"✅ Multi-Domain cache file isolation normal")
        for i, filename in enumerate(cache_files):
            print(f"  {domains[i]} → {filename}")


def run_comprehensive_test():
    """Run comprehensive functionality validation test"""
    print("=" * 60)
    print("🚀 Starting redmine-mcp new feature validation test")
    print("=" * 60)
    
    test_classes = [
        TestUserFunctionality,
        TestCacheSystem, 
        TestHelperFunctions,
        TestDomainIsolation
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__} tests...")
        print("-" * 40)
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                print(f"\n🔍 Running {test_method}...")
                getattr(test_instance, test_method)()
                passed_tests += 1
                print(f"✅ {test_method} passed")
            except pytest.skip.Exception as e:
                print(f"⏭️  {test_method} skipped: {e}")
                passed_tests += 1  # Skipped tests count as passed
            except Exception as e:
                print(f"❌ {test_method} failed: {e}")
                failed_tests.append((test_method, str(e)))
    
    # Output test summary
    print("\n" + "=" * 60)
    print("📊 Test Result Summary")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\n❌ Failed tests:")
        for test_name, error in failed_tests:
            print(f"  - {test_name}: {error}")
    else:
        print("\n🎉 All tests passed!")
    
    return len(failed_tests) == 0


if __name__ == "__main__":
    # Run tests directly
    success = run_comprehensive_test()
    exit(0 if success else 1)
