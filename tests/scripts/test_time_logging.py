#!/usr/bin/env python3
"""
Test time logging functionality
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
    
    # Mock time entry activity data
    mock_client.get_available_time_entry_activities.return_value = {
        'Design': 10, 'Development': 11, 'Debugging': 12, 'Investigation': 13, 'Discussion': 14,
        'Testing': 15, 'Maintenance': 16, 'Documentation': 17, 'Teaching': 18, 'Translation': 19, 'Other': 20
    }
    
    # Mock helper functions
    mock_client.find_time_entry_activity_id_by_name.side_effect = lambda name: {
        'Design': 10, 'Development': 11, 'Debugging': 12, 'Investigation': 13, 'Discussion': 14,
        'Testing': 15, 'Maintenance': 16, 'Documentation': 17, 'Teaching': 18, 'Translation': 19, 'Other': 20
    }.get(name)
    
    # Mock time entry creation
    mock_client.create_time_entry.return_value = 123  # Time entry ID
    
    # Mock issue update
    mock_client.update_issue.return_value = None
    
    # Mock issue data
    mock_issue = MagicMock()
    mock_issue.subject = "Test issue"
    mock_client.get_issue.return_value = mock_issue
    
    return mock_client


def test_add_note_with_time_logging():
    """Test adding note and logging time"""
    print("⏰ Test adding note and logging time")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import add_issue_note
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # Test logging time using activity name
            result = add_issue_note(
                issue_id=1,
                notes="Feature development completed",
                spent_hours=2.5,
                activity_name="Development"
            )
            
            if "Note added successfully" in result and "Time record added successfully" in result:
                print("✅ Using activity name to log time normal")
                print(f"   Result contains time entry ID: {'Time entry ID: 123' in result}")
                print(f"   Result contains hours: {'2.5 hours' in result}")
                print(f"   Result contains activity: {'Development' in result}")
            else:
                print(f"❌ Using activity name to log time abnormal: {result}")
                return False
            
            # Verify related methods were called
            mock_client.find_time_entry_activity_id_by_name.assert_called_with("Development")
            mock_client.create_time_entry.assert_called()
            mock_client.update_issue.assert_called()
            
            # Test logging time using activity ID
            result = add_issue_note(
                issue_id=1,
                notes="Fix bug",
                spent_hours=1.0,
                activity_id=12
            )
            
            if "Note added successfully" in result and "Time record added successfully" in result:
                print("✅ Using activity ID to log time normal")
            else:
                print(f"❌ Using activity ID to log time abnormal: {result}")
                return False
            
            # Test invalid activity name
            result = add_issue_note(
                issue_id=1,
                notes="Test note",
                spent_hours=1.0,
                activity_name="NonExistentActivity"
            )
            
            if "Time tracking activity name not found" in result and "Available activities" in result:
                print("✅ Invalid activity name error handling normal")
            else:
                print(f"❌ Invalid activity name error handling abnormal: {result}")
                return False
            
            # Test invalid hours
            result = add_issue_note(
                issue_id=1,
                notes="Test note",
                spent_hours=0,
                activity_name="Development"
            )
            
            if "Hours spent must be greater than 0" in result:
                print("✅ Invalid hours error handling normal")
            else:
                print(f"❌ Invalid hours error handling abnormal: {result}")
                return False
            
            # Test missing activity parameter
            result = add_issue_note(
                issue_id=1,
                notes="Test note",
                spent_hours=1.0
            )
            
            if "must be provided" in result:
                print("✅ Missing activity parameter error handling normal")
            else:
                print(f"❌ Missing activity parameter error handling abnormal: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_note_only():
    """Test adding note only (backwards compatibility)"""
    print("\n📝 Test adding note only (backwards compatibility)")
    print("-" * 40)
    
    try:
        from redmine_mcp.server import add_issue_note
        
        mock_client = create_mock_client()
        
        with patch('redmine_mcp.server.get_client', return_value=mock_client):
            # Test adding note only
            result = add_issue_note(
                issue_id=1,
                notes="Add note only"
            )
            
            if "Note added successfully" in result and "Time record added successfully" not in result:
                print("✅ Add note only function normal")
            else:
                print(f"❌ Add note only function abnormal: {result}")
                return False
            
            # Verify time entry methods were not called
            mock_client.create_time_entry.assert_not_called()
            
            # Test private note
            result = add_issue_note(
                issue_id=1,
                notes="Private note",
                private=True
            )
            
            if "Note added successfully" in result and "private" in result:
                print("✅ Private note function normal")
            else:
                print(f"❌ Private note function abnormal: {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_time_activities():
    """Test time entry activity cache functionality"""
    print("\n💾 Test time entry activity cache functionality")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        
        mock_time_activities = [
            {'id': 10, 'name': 'Design'},
            {'id': 11, 'name': 'Development'},
            {'id': 12, 'name': 'Debugging'},
            {'id': 13, 'name': 'Investigation'},
            {'id': 14, 'name': 'Discussion'},
            {'id': 15, 'name': 'Testing'},
            {'id': 16, 'name': 'Maintenance'},
            {'id': 17, 'name': 'Documentation'},
            {'id': 18, 'name': 'Teaching'},
            {'id': 19, 'name': 'Translation'},
            {'id': 20, 'name': 'Other'}
        ]
        
        client = get_client()
        
        # Set up mock cache
        client._enum_cache = {
            'cache_time': 1234567890,
            'domain': 'http://localhost:3000',
            'priorities': {},
            'statuses': {},
            'trackers': {},
            'time_entry_activities': {item['name']: item['id'] for item in mock_time_activities},
            'users_by_name': {},
            'users_by_login': {}
        }
        
        # Test lookup functions
        test_cases = [
            ('find_time_entry_activity_id_by_name', 'Development', 11),
            ('find_time_entry_activity_id_by_name', 'Testing', 15),
            ('find_time_entry_activity_id_by_name', 'NonExistentActivity', None),
        ]
        
        for method_name, input_value, expected in test_cases:
            method = getattr(client, method_name)
            result = method(input_value)
            
            if result == expected:
                print(f"✅ {method_name}('{input_value}') → {result}")
            else:
                print(f"❌ {method_name}('{input_value}') → {result}, expected {expected}")
                return False
        
        # Test getting all activities
        activities = client.get_available_time_entry_activities()
        if len(activities) == 11 and activities.get('Development') == 11:
            print(f"✅ get_available_time_entry_activities: {len(activities)} activities")
        else:
            print(f"❌ get_available_time_entry_activities error: {activities}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_time_entry_creation():
    """Test time entry creation functionality"""
    print("\n🆕 Test time entry creation functionality")
    print("-" * 40)
    
    try:
        from redmine_mcp.redmine_client import get_client
        from datetime import date
        
        client = get_client()
        
        # Mock _make_request method
        def mock_make_request(method, endpoint, **kwargs):
            if endpoint == '/time_entries.json' and method == 'POST':
                return {'time_entry': {'id': 456}}
            else:
                raise Exception(f"Unexpected request: {method} {endpoint}")
        
        with patch.object(client, '_make_request', side_effect=mock_make_request):
            # Test creating time entry
            time_entry_id = client.create_time_entry(
                issue_id=1,
                hours=2.5,
                activity_id=11,
                comments="Develop new feature"
            )
            
            if time_entry_id == 456:
                print("✅ Create time entry function normal")
            else:
                print(f"❌ Create time entry function abnormal: {time_entry_id}")
                return False
            
            # Test time entry with specified date
            time_entry_id = client.create_time_entry(
                issue_id=1,
                hours=1.0,
                activity_id=12,
                comments="Fix bug",
                spent_on="2025-06-25"
            )
            
            if time_entry_id == 456:
                print("✅ Specified date time entry function normal")
            else:
                print(f"❌ Specified date time entry function abnormal: {time_entry_id}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_time_logging_tests():
    """Run all time logging tests"""
    print("🧪 redmine-mcp time logging functionality test")
    print("=" * 60)
    
    tests = [
        ("Time entry activity cache", test_cache_time_activities),
        ("Time entry creation", test_time_entry_creation),
        ("Add note and log time", test_add_note_with_time_logging),
        ("Add note only (backwards compatible)", test_add_note_only),
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
    print("📊 Time logging functionality test result summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ Passed" if success else "❌ Failed"
        print(f"{test_name:<30} {status}")
    
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All time logging functionality tests passed!")
        print("Now you can log time when adding issue notes!")
        print("\n💡 Usage examples:")
        print("- add_issue_note(issue_id=1, notes='Development completed', spent_hours=2.5, activity_name='Development')")
        print("- add_issue_note(issue_id=1, notes='Fix bug', spent_hours=1.0, activity_id=12)")
        print("- add_issue_note(issue_id=1, notes='Add note only')  # Backwards compatible")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed, please check time logging functionality")
        return False


if __name__ == "__main__":
    success = run_time_logging_tests()
    sys.exit(0 if success else 1)
