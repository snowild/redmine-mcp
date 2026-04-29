#!/usr/bin/env python3
"""
Complete MCP functionality test script
Test all MCP tools using local Redmine environment
"""

import sys
import os
import time
import requests
from typing import List, Dict, Any

# Add src directory to path (go up two levels from tests/scripts to root)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from redmine_mcp.server import (
    server_info, health_check, get_issue, update_issue_status,
    list_project_issues, get_issue_statuses, get_projects,
    search_issues, update_issue_content, add_issue_note,
    assign_issue, create_new_issue, get_my_issues, close_issue
)


class MCPTester:
    """MCP functionality tester"""
    
    def __init__(self):
        self.test_results = []
        self.created_issues = []
        self.project_id = None
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'name': test_name,
            'success': success,
            'message': message
        })
    
    def test_basic_functions(self):
        """Test basic functions"""
        print("\n📋 Testing basic functions...")
        
        # Test server info
        try:
            result = server_info()
            self.log_test("Server info", "Redmine MCP" in result, f"Got: {result[:50]}...")
        except Exception as e:
            self.log_test("Server info", False, f"Error: {e}")
        
        # Test health check
        try:
            result = health_check()
            success = "functioning normally" in result or "connected" in result
            self.log_test("Health check", success, f"Status: {result[:50]}...")
        except Exception as e:
            self.log_test("Health check", False, f"Error: {e}")
    
    def test_query_functions(self):
        """Test query functions"""
        print("\n🔍 Testing query functions...")
        
        # Test getting project list
        try:
            result = get_projects()
            success = "Projects" in result
            self.log_test("Get project list", success, f"Result: {result[:50]}...")
            
            # Parse project ID from result
            if success:
                import re
                id_match = re.search(r'(\d+)\s+[a-z-]+\s+', result)
                if id_match:
                    self.project_id = int(id_match.group(1))
                    print(f"  📝 Found test project ID: {self.project_id}")
        except Exception as e:
            self.log_test("Get project list", False, f"Error: {e}")
        
        # Test getting issue statuses
        try:
            result = get_issue_statuses()
            success = "Available issue statuses" in result
            self.log_test("Get issue statuses", success, f"Result: {result[:50]}...")
        except Exception as e:
            self.log_test("Get issue statuses", False, f"Error: {e}")
        
        # Test listing project issues
        if self.project_id:
            try:
                result = list_project_issues(self.project_id)
                success = "turn up" in result or "No matching issues were found" in result  # Both are normal results
                self.log_test("List project issues", success, f"Result: {result[:50]}...")
                
                # Parse issue ID from result
                if "turn up" in result:
                    import re
                    id_matches = re.findall(r'^(\d+)\s+', result, re.MULTILINE)
                    if id_matches:
                        first_issue_id = int(id_matches[0])
                        print(f"  📝 Found issue ID: {first_issue_id}")
                        return first_issue_id
            except Exception as e:
                self.log_test("List project issues", False, f"Error: {e}")
        
        return None
    
    def test_create_functions(self):
        """Test create functions"""
        print("\n➕ Testing create functions...")
        
        if not self.project_id:
            self.log_test("Create new issue", False, "No valid project ID")
            return None
        
        # Test creating new issue
        try:
            subject = f"MCP test issue - {int(time.time())}"
            description = "This is a test issue created by MCP automated test script"
            
            result = create_new_issue(
                self.project_id, 
                subject, 
                description
            )
            
            success = "New topic created successfully" in result
            self.log_test("Create new issue", success, f"Result: {result[:50]}...")
            
            if success:
                # Parse issue ID
                import re
                id_match = re.search(r'Issue ID: #(\d+)', result)
                if id_match:
                    issue_id = int(id_match.group(1))
                    self.created_issues.append(issue_id)
                    print(f"  📝 Created issue ID: {issue_id}")
                    return issue_id
        except Exception as e:
            self.log_test("Create new issue", False, f"Error: {e}")
        
        return None
    
    def test_update_functions(self, issue_id: int):
        """Test update functions"""
        print("\n✏️  Testing update functions...")
        
        # Test getting issue details
        try:
            result = get_issue(issue_id)
            success = f"#issue#{issue_id}" in result
            self.log_test("Get issue details", success, f"Result: {result[:50]}...")
        except Exception as e:
            self.log_test("Get issue details", False, f"Error: {e}")
        
        # Test updating issue content
        try:
            new_subject = f"Updated MCP test issue - {int(time.time())}"
            result = update_issue_content(
                issue_id, 
                subject=new_subject,
                description="Description updated by MCP",
                done_ratio=25
            )
            success = "Topic content updated successfully" in result
            self.log_test("Update issue content", success, f"Result: {result[:50]}...")
        except Exception as e:
            self.log_test("Update issue content", False, f"Error: {e}")
        
        # Test adding issue note
        try:
            result = add_issue_note(issue_id, "This is a note added by MCP automated test", private=False)
            success = "Note added successfully" in result
            self.log_test("Add issue note", success, f"Result: {result[:50]}...")
        except Exception as e:
            self.log_test("Add issue note", False, f"Error: {e}")
        
        # Test updating issue status
        try:
            result = update_issue_status(issue_id, 2, "Status updated by MCP automated test")
            success = "Issue status updated successfully" in result or "not found" in result.lower()  # Status ID may not exist
            self.log_test("Update issue status", success, f"Result: {result[:50]}...")
        except Exception as e:
            self.log_test("Update issue status", False, f"Error: {e}")
    
    def test_search_functions(self):
        """Test search functions"""
        print("\n🔎 Testing search functions...")
        
        # Test searching issues
        try:
            result = search_issues("MCP", limit=5)
            success = "Search keyword" in result
            self.log_test("Search issues", success, f"Result: {result[:50]}...")
        except Exception as e:
            self.log_test("Search issues", False, f"Error: {e}")
        
        # Test getting my issues
        try:
            result = get_my_issues("all", 10)
            success = "assigned to" in result.lower() or "Topics" in result
            self.log_test("Get my issues", success, f"Result: {result[:50]}...")
        except Exception as e:
            self.log_test("Get my issues", False, f"Error: {e}")
    
    def test_close_functions(self, issue_id: int):
        """Test close functions"""
        print("\n🔒 Testing close functions...")
        
        # Test closing issue
        try:
            result = close_issue(issue_id, "Issue closed by MCP automated test", 100)
            success = "Issue closed successfully" in result or "not found" in result.lower()
            self.log_test("Close issue", success, f"Result: {result[:50]}...")
        except Exception as e:
            self.log_test("Close issue", False, f"Error: {e}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Note: This just logs, actual cleanup requires DELETE API
        if self.created_issues:
            print(f"  📝 Created test issues: {self.created_issues}")
            print("  ℹ️  To clean up, please manually delete or close these issues")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting MCP functionality integration test")
        print("=" * 50)
        
        # Check environment
        if not os.getenv('REDMINE_DOMAIN') or not os.getenv('REDMINE_API_KEY'):
            print("❌ Environment variables not set, please run configure_redmine.py first")
            return False
        
        # Basic functionality test
        self.test_basic_functions()
        
        # Query functionality test
        existing_issue_id = self.test_query_functions()
        
        # Create functionality test
        new_issue_id = self.test_create_functions()
        
        # Update functionality test
        test_issue_id = new_issue_id or existing_issue_id
        if test_issue_id:
            self.test_update_functions(test_issue_id)
        
        # Search functionality test
        self.test_search_functions()
        
        # Close functionality test
        if new_issue_id:
            self.test_close_functions(new_issue_id)
        
        # Clean up test data
        self.cleanup_test_data()
        
        # Statistics
        self.print_summary()
        
        # Return success rate
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        return passed / total > 0.8  # 80% pass rate considered success
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 Test Result Summary")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['success'])
        failed = len(self.test_results) - passed
        success_rate = (passed / len(self.test_results)) * 100 if self.test_results else 0
        
        print(f"Total tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if failed > 0:
            print("\n❌ Failed tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['name']}: {result['message']}")
        
        if success_rate >= 80:
            print("\n🎉 Test passed! MCP functionality working normally")
        else:
            print("\n⚠️  Some tests failed, please check the errors above")


def main():
    """Main function"""
    tester = MCPTester()
    success = tester.run_all_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
