"""
Advanced MCP tool tests
"""

import os
import pytest
from unittest.mock import patch, Mock
from redmine_mcp.server import (
    update_issue_content, add_issue_note, assign_issue,
    create_new_issue, get_my_issues, close_issue
)
from redmine_mcp.redmine_client import RedmineIssue, RedmineProject


class TestAdvancedMCPTools:
    """Advanced MCP tool tests"""
    
    def setup_method(self):
        """Setup before each test"""
        # Ensure test environment variables are set
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            pass
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_success(self, mock_get_client):
        """Test updating issue content successfully"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        # Simulate updated issue
        updated_issue = RedmineIssue(
            id=123,
            subject='Updated Title',
            description='Updated Description',
            status={'name': 'In Progress'},
            priority={'name': 'High'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': 'Test User'},
            done_ratio=75
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(
            123, 
            subject="Updated Title", 
            description="Updated Description",
            done_ratio=75
        )
        
        assert "Issue content updated successfully!" in result
        assert "Updated Title" in result
        assert "Subject: Updated Title" in result
        assert "Description updated" in result
        assert "Done ratio: 75%" in result
        
        # Validate call arguments
        mock_client.update_issue.assert_called_once_with(
            123, 
            subject="Updated Title",
            description="Updated Description",
            done_ratio=75
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_no_params(self, mock_get_client):
        """Test updating issue content with no parameters"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123)
        
        assert "Error: Please provide at least one field to update" in result
        mock_client.update_issue.assert_not_called()
    
    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_invalid_done_ratio(self, mock_get_client):
        """Test updating issue content with invalid done ratio"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = update_issue_content(123, done_ratio=150)
        
        assert "Error: Complete percentage must be between 0-100" in result
        mock_client.update_issue.assert_not_called()
    
    @patch('redmine_mcp.server.get_client')
    def test_add_issue_note_success(self, mock_get_client):
        """Test adding issue note successfully"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        mock_issue = RedmineIssue(
            id=123,
            subject='Test Issue',
            description='Description',
            status={'name': 'New'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': 'Test User'}
        )
        mock_client.get_issue.return_value = mock_issue
        mock_get_client.return_value = mock_client
        
        result = add_issue_note(123, "This is a test note", private=True)
        
        assert "Note added successfully!" in result
        assert "This is a test note" in result
        assert "private" in result
        
        # Validate call arguments
        mock_client.update_issue.assert_called_once_with(
            123, 
            notes="This is a test note",
            private_notes=True
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_add_issue_note_empty_notes(self, mock_get_client):
        """Test adding issue note with empty content"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = add_issue_note(123, "  ")
        
        assert "Error: Note content cannot be empty" in result
        mock_client.update_issue.assert_not_called()
    
    @patch('redmine_mcp.server.get_client')
    def test_assign_issue_success(self, mock_get_client):
        """Test assigning issue successfully"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='Test Issue',
            description='Description',
            status={'name': 'New'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': 'Test User'},
            assigned_to={'name': 'Assigned User', 'id': 456}
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = assign_issue(123, 456, notes="Assign to test user")
        
        assert "Topic assignment updated successfully!" in result
        assert "Action: Assigned to user ID 456" in result
        assert "Assigned User" in result
        assert "Assign to test user" in result
        
        # Validate call arguments
        mock_client.update_issue.assert_called_once_with(
            123, 
            assigned_to_id=456,
            notes="Assign to test user"
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_assign_issue_unassign(self, mock_get_client):
        """Test unassigning issue"""
        mock_client = Mock()
        mock_client.update_issue.return_value = True
        
        updated_issue = RedmineIssue(
            id=123,
            subject='Test Issue',
            description='Description',
            status={'name': 'New'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': 'Test User'},
            assigned_to=None
        )
        mock_client.get_issue.return_value = updated_issue
        mock_get_client.return_value = mock_client
        
        result = assign_issue(123, None)
        
        assert "Topic assignment updated successfully!" in result
        assert "Unassign" in result
        assert "Not assigned" in result
        
        # Validate call arguments
        mock_client.update_issue.assert_called_once_with(123, assigned_to_id=None)
    
    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_success(self, mock_get_client):
        """Test creating new issue successfully"""
        mock_client = Mock()
        mock_client.create_issue.return_value = 789
        
        new_issue = RedmineIssue(
            id=789,
            subject='New Issue Title',
            description='New Issue Description',
            status={'name': 'New'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Feature'},
            author={'name': 'Creator'},
            assigned_to={'name': 'Assigned User'}
        )
        mock_client.get_issue.return_value = new_issue
        mock_get_client.return_value = mock_client
        
        result = create_new_issue(
            1, 
            "New Issue Title", 
            "New Issue Description",
            tracker_id=2,
            assigned_to_id=456
        )
        
        assert "New issue created successfully!" in result
        assert "Issue ID: #789" in result
        assert "Subject: New Issue Title" in result
        assert "Project: Test Project" in result
        assert "New Issue Description" in result
        
        # Validate call arguments
        mock_client.create_issue.assert_called_once_with(
            project_id=1,
            subject="New Issue Title",
            description="New Issue Description",
            tracker_id=2,
            priority_id=None,
            assigned_to_id=456,
            parent_issue_id=None,
            status_id=None,
            start_date=None,
            due_date=None,
            estimated_hours=None,
            category_id=None
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_empty_subject(self, mock_get_client):
        """Test creating new issue with empty subject"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        result = create_new_issue(1, "  ")
        
        assert "Error: Issue title cannot be empty" in result
        mock_client.create_issue.assert_not_called()
    
    @patch('redmine_mcp.server.get_client')
    def test_get_my_issues_success(self, mock_get_client):
        """Test getting my issues successfully"""
        mock_client = Mock()
        
        # Simulate current user
        mock_client.get_current_user.return_value = {
            'id': 123,
            'firstname': 'Test',
            'lastname': 'User'
        }
        
        # Simulate issue list
        mock_issues = [
            RedmineIssue(
                id=101,
                subject='My Issue 1',
                description='Description 1',
                status={'name': 'In Progress'},
                priority={'name': 'Normal'},
                project={'name': 'Project A', 'id': 1},
                tracker={'name': 'Bug'},
                author={'name': 'Other User'},
                updated_on='2024-01-01'
            )
        ]
        mock_client.list_issues.return_value = mock_issues
        mock_get_client.return_value = mock_client
        
        result = get_my_issues("open", 10)
        
        assert "Issues assigned to Test User:" in result
        assert "Status filter: open" in result
        assert "Found 1 issues:" in result
        assert "My Issue 1" in result
        
        # Validate call arguments
        mock_client.list_issues.assert_called_once_with(
            assigned_to_id=123,
            limit=10,
            sort='updated_on:desc',
            status_id='o'
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_close_issue_success(self, mock_get_client):
        """Test closing issue successfully"""
        mock_client = Mock()
        
        # Simulate status list
        mock_client.get_issue_statuses.return_value = [
            {'id': 1, 'name': 'New', 'is_closed': False},
            {'id': 5, 'name': 'Closed', 'is_closed': True}
        ]
        
        mock_client.update_issue.return_value = True
        
        closed_issue = RedmineIssue(
            id=123,
            subject='Closed Issue',
            description='Description',
            status={'name': 'Closed'},
            priority={'name': 'Normal'},
            project={'name': 'Test Project', 'id': 1},
            tracker={'name': 'Bug'},
            author={'name': 'Test User'},
            done_ratio=100
        )
        mock_client.get_issue.return_value = closed_issue
        mock_get_client.return_value = mock_client
        
        result = close_issue(123, "Issue completed", 100)
        
        assert "Issue closed successfully!" in result
        assert "Closed Issue" in result
        assert "Status: Closed" in result
        assert "Done ratio: 100%" in result
        assert "Close Notes: Issue completed" in result
        
        # Validate call arguments
        mock_client.update_issue.assert_called_once_with(
            123,
            status_id=5,
            done_ratio=100,
            notes="Issue completed"
        )
    
    @patch('redmine_mcp.server.get_client')
    def test_close_issue_no_closed_status(self, mock_get_client):
        """Test closing issue when no closed status is found"""
        mock_client = Mock()
        
        # Simulate no closed status
        mock_client.get_issue_statuses.return_value = [
            {'id': 1, 'name': 'New', 'is_closed': False},
            {'id': 2, 'name': 'In Progress', 'is_closed': False}
        ]
        
        mock_get_client.return_value = mock_client
        
        result = close_issue(123)
        
        assert "Error: No available shutdown status found" in result
        mock_client.update_issue.assert_not_called()
