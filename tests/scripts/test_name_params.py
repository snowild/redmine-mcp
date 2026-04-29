#!/usr/bin/env python3
"""
Test MCP tool name parameter support
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


def create_mock_client():
    """Create mock client"""
    mock_client = MagicMock()
    
    # Mock cache data
    mock_client.get_available_priorities.return_value = {
        'Low': 5, 'Normal': 6, 'High': 7, 'Urgent': 8
    }
    mock_client.get_available_statuses.return_value = {
        'New': 1, 'In Progress': 2, 'Resolved': 3, 'Closed': 4
    }
    mock_client.get_available_trackers.return_value = {
        'Bug': 1, 'Feature': 2, 'Support': 3
    }
    mock_client.get_available_users.return_value = {
        'by_name': {'Redmine Admin': 1, 'Test User': 2},
        'by_login': {'admin': 1, 'user1': 2}
    }
    
    # Mock helper functions
    mock_client.find_priority_id_by_name.side_effect = lambda name: {
        'Low': 5, 'Normal': 6, 'High': 7, 'Urgent': 8
    }.get(name)
    
    mock_client.find_status_id_by_name.side_effect = lambda name: {
        'New': 1, 'In Progress': 2, 'Resolved': 3, 'Closed': 4
    }.get(name)
    
    mock_client.find_tracker_id_by_name.side_effect = lambda name: {
        'Bug': 1, 'Feature': 2, 'Support': 3
    }.get(name)
    
    mock_client.find_user_id_by_name.side_effect = lambda name: {
        'Redmine Admin': 1, 'Test User': 2
    }.get(name)
    
    mock_client.find_user_id_by_login.side_effect = lambda name: {
        'admin': 1, 'user1': 2
    }.get(name)
    
    # Mock update operations
    mock_client.update_issue.return_value = None
    mock_client.create_issue.return_value = 999  # New issue ID
    
    # Mock issue data
    mock_issue = MagicMock()
    mock_issue.subject = "Test issue"
    mock_issue.status = {'name': 'In Progress'}
    mock_issue.priority = {'name': 'High'}
    mock_issue.tracker = {'name': 'Bug'}
    mock_issue.assigned_to = {'name': 'Redmine Admin'}
    mock_client.get_issue.return_value = mock_issue
    
    return mock_client


def test_update_issue_status_with_name():
    """Test updating issue status using name"""
    print("🔄 Test update_issue_status name parameter")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import update_issue_status
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # Test valid status name
            result = update_issue_status(issue_id=1, status_name="In Progress", notes="Update status using name")
            
            if "successfully" in result.lower():
                print("✅ Valid status name handling normal")
            else:
                print(f"❌ Valid status name handling abnormal: {result}")
                return False
            
            # Verify helper function was called
            mock_client.find_status_id_by_name.assert_called_with("In Progress")
            mock_client.update_issue.assert_called()
            
            # Test invalid status name
            result = update_issue_status(issue_id=1, status_name="NonExistentStatus")
            
            if "Status name not found" in result and "Available status" in result:
                print("✅ Invalid status name error handling normal")
            else:
                print(f"❌ Invalid status name error handling abnormal: {result}")
                return False
            
            # Test no parameter provided
            result = update_issue_status(issue_id=1)
            
            if "must be supplied" in result:
                print("✅ Parameter validation normal")
            else:
                print(f"❌ Parameter validation abnormal: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_update_issue_content_with_names():
    """Test updating issue content using names"""
    print("\n📝 Test update_issue_content name parameters")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import update_issue_content
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # Test valid name parameters
            result = update_issue_content(
                issue_id=1,
                priority_name="High",
                tracker_name="Bug",
                subject="Updated title"
            )
            
            if "successfully" in result.lower():
                print("✅ Valid name parameter handling normal")
                
                # Verify helper functions were called
                mock_client.find_priority_id_by_name.assert_called_with("High")
                mock_client.find_tracker_id_by_name.assert_called_with("Bug")
                
            else:
                print(f"❌ Valid name parameter handling abnormal: {result}")
                return False
            
            # Test invalid priority name
            result = update_issue_content(issue_id=1, priority_name="NonExistentPriority")
            
            if "Priority name not found" in result and "Available priorities" in result:
                print("✅ Invalid priority name error handling normal")
            else:
                print(f"❌ Invalid priority name error handling abnormal: {result}")
                return False
            
            # Test invalid tracker name
            result = update_issue_content(issue_id=1, tracker_name="NonExistentTracker")
            
            if "Tracker name not found" in result and "Available trackers" in result:
                print("✅ Invalid tracker name error handling normal")
            else:
                print(f"❌ Invalid tracker name error handling abnormal: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_assign_issue_with_names():
    """Test assigning issue using names"""
    print("\n👤 Test assign_issue name parameters")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import assign_issue
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # Test valid user name
            result = assign_issue(issue_id=1, user_name="Redmine Admin", notes="Assign using name")
            
            if "successfully" in result.lower():
                print("✅ Valid user name handling normal")
                mock_client.find_user_id_by_name.assert_called_with("Redmine Admin")
            else:
                print(f"❌ Valid user name handling abnormal: {result}")
                return False
            
            # Test valid user login
            result = assign_issue(issue_id=1, user_login="admin", notes="Assign using login")
            
            if "successfully" in result.lower():
                print("✅ Valid user login handling normal")
                mock_client.find_user_id_by_login.assert_called_with("admin")
            else:
                print(f"❌ Valid user login handling abnormal: {result}")
                return False
            
            # Test invalid user name
            result = assign_issue(issue_id=1, user_name="Non-existent user")
            
            if "Username not found" in result and "Available users" in result:
                print("✅ Invalid user name error handling normal")
            else:
                print(f"❌ Invalid user name error handling abnormal: {result}")
                return False
            
            # Test invalid user login
            result = assign_issue(issue_id=1, user_login="NonExistentUser")
            
            if "User login name not found" in result and "Available users" in result:
                print("✅ Invalid user login error handling normal")
            else:
                print(f"❌ Invalid user login error handling abnormal: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_new_issue_with_names():
    """Test creating new issue using names"""
    print("\n➕ Test create_new_issue name parameters")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import create_new_issue
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # Test valid name parameters
            result = create_new_issue(
                project_id=1,
                subject="New test issue",
                description="Created using name parameters",
                priority_name="High",
                tracker_name="Feature",
                assigned_to_name="Redmine Admin"
            )
            
            if "successfully" in result.lower():
                print("✅ Valid name parameter creation normal")
                
                # Verify helper functions were called
                mock_client.find_priority_id_by_name.assert_called_with("High")
                mock_client.find_tracker_id_by_name.assert_called_with("Feature")
                mock_client.find_user_id_by_name.assert_called_with("Redmine Admin")
                
                # Verify correct IDs were used when creating issue
                mock_client.create_issue.assert_called_with(
                    project_id=1,
                    subject="New test issue",
                    description="Created using name parameters",
                    tracker_id=2,    # Feature ID
                    priority_id=7,   # High ID  
                    assigned_to_id=1 # Redmine Admin ID
                )
                
            else:
                print(f"❌ Valid name parameter creation abnormal: {result}")
                return False
            
            # Test using login for assignment
            result = create_new_issue(
                project_id=1,
                subject="Another test issue",
                assigned_to_login="admin"
            )
            
            if "successfully" in result.lower():
                print("✅ Using login assignment normal")
                mock_client.find_user_id_by_login.assert_called_with("admin")
            else:
                print(f"❌ Using login assignment abnormal: {result}")
                return False
            
            # Test invalid parameters
            test_cases = [
                ("Invalid priority", {"priority_name": "NonExistentPriority"}, "Priority name not found"),
                ("Invalid tracker", {"tracker_name": "NonExistentTracker"}, "Tracker name not found"),
                ("Invalid user name", {"assigned_to_name": "NonExistentUser"}, "Username not found"),
                ("Invalid user login", {"assigned_to_login": "nonexistent"}, "User login name not found"),
            ]
            
            for test_name, kwargs, expected_error in test_cases:
                result = create_new_issue(project_id=1, subject="Test issue", **kwargs)
                if expected_error in result:
                    print(f"✅ {test_name} error handling normal")
                else:
                    print(f"❌ {test_name} error handling abnormal: {result}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backwards_compatibility():
    """Test backwards compatibility"""
    print("\n🔄 Test backwards compatibility")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import update_issue_status, update_issue_content, assign_issue, create_new_issue
        from redmine_mcp.redmine_client import get_client
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # Test using original ID parameters still works
            
            # Update status
            result = update_issue_status(issue_id=1, status_id=2, notes="Update using ID")
            if "successfully" in result.lower():
                print("✅ update_issue_status ID parameter backwards compatible")
            else:
                print(f"❌ update_issue_status ID parameter not compatible: {result}")
                return False
            
            # Update content
            result = update_issue_content(issue_id=1, priority_id=7, tracker_id=1)
            if "successfully" in result.lower():
                print("✅ update_issue_content ID parameter backwards compatible")
            else:
                print(f"❌ update_issue_content ID parameter not compatible: {result}")
                return False
            
            # Assign issue
            result = assign_issue(issue_id=1, user_id=1, notes="Assign using ID")
            if "successfully" in result.lower():
                print("✅ assign_issue ID parameter backwards compatible")
            else:
                print(f"❌ assign_issue ID parameter not compatible: {result}")
                return False
            
            # Create issue
            result = create_new_issue(
                project_id=1,
                subject="ID parameter test",
                tracker_id=2,
                priority_id=6,
                assigned_to_id=1
            )
            if "successfully" in result.lower():
                print("✅ create_new_issue ID parameter backwards compatible")
            else:
                print(f"❌ create_new_issue ID parameter not compatible: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_name_params_tests():
    """Run all name parameter tests"""
    print("🧪 redmine-mcp name parameter support test")
    print("=" * 60)
    
    tests = [
        ("update_issue_status name parameter", test_update_issue_status_with_name),
        ("update_issue_content name parameter", test_update_issue_content_with_names),
        ("assign_issue name parameter", test_assign_issue_with_names),
        ("create_new_issue name parameter", test_create_new_issue_with_names),
        ("Backwards compatibility", test_backwards_compatibility),
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
    print("📊 Name parameter support test result summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ Passed" if success else "❌ Failed"
        print(f"{test_name:<35} {status}")
    
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All name parameter support tests passed!")
        print("MCP tools now fully support name parameters while maintaining backwards compatibility!")
        print("\n💡 Usage examples:")
        print("- update_issue_status(issue_id=1, status_name='In Progress')")
        print("- assign_issue(issue_id=1, user_name='Redmine Admin')")
        print("- create_new_issue(project_id=1, subject='test', priority_name='High')")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed, please check name parameter functionality")
        return False


if __name__ == "__main__":
    success = run_name_params_tests()
    sys.exit(0 if success else 1)
