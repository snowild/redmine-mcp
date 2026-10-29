"""
Advanced MCP tool tests
"""

import os
import pytest
from unittest.mock import patch, Mock
from redmine_mcp.server import (
    update_issue_content, add_issue_note, assign_issue,
    create_new_issue, get_my_issues, close_issue,
    attach_files_to_issue
)
from redmine_mcp.redmine_client import RedmineIssue, RedmineProject, RedmineAPIError


class TestAdvancedMCPTools:
    """Advanced MCP tool tests"""
    
    def setup_method(self):
        """Setup before each test"""
        # Ensure test environment variables are set
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }, clear=True):
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

    def _version_client(self, mock_get_client):
        mock_client = Mock()
        mock_client.get_issue.return_value = RedmineIssue(
            id=123, subject='T', description='', status={'name': 'New'},
            priority={'name': 'Normal'}, project={'name': 'P', 'id': 1},
            tracker={'name': 'Bug'}, author={'name': 'U'})
        mock_client.get_versions.return_value = [{'id': 7, 'name': 'v1.0'}, {'id': 8, 'name': 'v2.0'}]
        mock_get_client.return_value = mock_client
        return mock_client

    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_version_id(self, mock_get_client):
        """Test updating target version by ID"""
        mock_client = self._version_client(mock_get_client)

        result = update_issue_content(123, version_id=8)

        assert "Target version ID: 8" in result
        mock_client.update_issue.assert_called_once_with(123, fixed_version_id=8)

    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_version_name(self, mock_get_client):
        """Test updating target version by name"""
        mock_client = self._version_client(mock_get_client)

        result = update_issue_content(123, version_name="v1.0")

        assert "Target version ID: 7" in result
        mock_client.get_versions.assert_called_once_with(1)
        mock_client.update_issue.assert_called_once_with(123, fixed_version_id=7)

    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_version_name_not_found(self, mock_get_client):
        """Test unknown version name lists available versions"""
        mock_client = self._version_client(mock_get_client)

        result = update_issue_content(123, version_name="v9")

        assert 'Version name not found or not open: "v9"' in result
        assert "- v1.0" in result and "- v2.0" in result
        mock_client.update_issue.assert_not_called()

    @patch('redmine_mcp.server.get_client')
    def test_update_issue_content_remove_version(self, mock_get_client):
        """Test clearing target version"""
        mock_client = self._version_client(mock_get_client)

        result = update_issue_content(123, remove_version=True)

        assert "Remove target version" in result
        mock_client.update_issue.assert_called_once_with(123, fixed_version_id=None)
    
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
            category_id=None,
            fixed_version_id=None,
            uploads=None
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
    def test_create_new_issue_with_files(self, mock_get_client, tmp_path):
        """Test creating an issue with attachments"""
        test_file = tmp_path / "spec.pdf"
        test_file.write_bytes(b"%PDF fake")

        uploads = [{'token': '3.ccc', 'filename': 'spec.pdf',
                    'content_type': 'application/pdf'}]
        mock_client = Mock()
        mock_client.upload_files.return_value = uploads
        mock_client.create_issue.return_value = 456

        mock_issue = Mock()
        mock_issue.subject = 'Issue with attachment'
        mock_issue.project = {'name': 'Test Project'}
        mock_issue.tracker = {'name': 'Bug'}
        mock_issue.status = {'name': 'New'}
        mock_issue.priority = {'name': 'Normal'}
        mock_issue.assigned_to = None
        mock_client.get_issue.return_value = mock_issue
        mock_get_client.return_value = mock_client

        result = create_new_issue(1, "Issue with attachment",
                                  file_paths=[str(test_file)])

        assert "New issue created successfully" in result
        assert "spec.pdf" in result
        mock_client.upload_files.assert_called_once_with([str(test_file)])
        assert mock_client.create_issue.call_args.kwargs['uploads'] == uploads

    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_with_version_id(self, mock_get_client):
        """Test creating an issue with target version ID"""
        mock_client = self._version_client(mock_get_client)
        mock_client.create_issue.return_value = 123

        result = create_new_issue(1, "Versioned", version_id=8)

        assert "New issue created successfully" in result
        assert mock_client.create_issue.call_args.kwargs['fixed_version_id'] == 8
        mock_client.get_versions.assert_not_called()

    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_with_version_name(self, mock_get_client):
        """Test creating an issue with target version name"""
        mock_client = self._version_client(mock_get_client)
        mock_client.create_issue.return_value = 123

        create_new_issue(1, "Versioned", version_name="v1.0")

        mock_client.get_versions.assert_called_once_with(1)
        assert mock_client.create_issue.call_args.kwargs['fixed_version_id'] == 7

    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_version_name_not_found(self, mock_get_client):
        """Test unknown version name aborts issue creation"""
        mock_client = self._version_client(mock_get_client)

        result = create_new_issue(1, "Versioned", version_name="v9")

        assert 'Version name not found or not open: "v9"' in result
        assert "- v1.0" in result and "- v2.0" in result
        mock_client.create_issue.assert_not_called()

    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_upload_failure_aborts(self, mock_get_client):
        """Test issue is not created when an upload fails"""
        mock_client = Mock()
        mock_client.upload_files.side_effect = RedmineAPIError(
            "File does not exist or is not a file: /no/such.txt"
        )
        mock_get_client.return_value = mock_client

        result = create_new_issue(1, "Doomed issue", file_paths=['/no/such.txt'])

        assert "Failed to create issue" in result
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
    def test_get_my_issues_includes_tracker_column(self, mock_get_client):
        """The table has a tracker column aligned with the dash row, so clients can filter by tracker"""
        mock_client = Mock()
        mock_client.get_current_user.return_value = {'id': 1, 'firstname': 'T', 'lastname': 'U'}
        mock_client.list_issues.return_value = [
            RedmineIssue(
                id=101, subject='My Issue', description=None,
                status={'name': '實作中'}, priority={'name': 'Normal'},
                project={'name': '專案甲', 'id': 1}, tracker={'name': 'Refactoring-long-name'},
                author={'name': 'X'}, updated_on='2024-01-01T00:00:00Z',
            )
        ]
        mock_get_client.return_value = mock_client

        lines = get_my_issues("open", 10).split('\n')
        dash = next(i for i, l in enumerate(lines) if l.startswith('-----'))
        widths = [len(seg) for seg in lines[dash].split(' ')]

        def cells(line):
            out, at = [], 0
            for i, w in enumerate(widths):
                end = len(line) if i == len(widths) - 1 else at + w
                out.append(line[at:end].strip())
                at = end + 1
            return out

        header = cells(lines[dash - 1])
        row = dict(zip(header, cells(lines[dash + 1])))
        assert 'tracker' in header
        assert row['tracker'] == 'Refactorin'  # truncated to the column width
        assert row['state'] == '實作中'
        assert row['Update time'] == '2024-01-01'

    @patch('redmine_mcp.server.get_client')
    def test_get_my_issues_includes_start_and_due_columns(self, mock_get_client):
        """start / due columns sit inside the dash-row widths; a missing date is an empty cell"""
        mock_client = Mock()
        mock_client.get_current_user.return_value = {'id': 1, 'firstname': 'T', 'lastname': 'U'}
        common = dict(description=None, status={'name': 'New'}, priority={'name': 'Normal'},
                      project={'name': 'P', 'id': 1}, tracker={'name': 'Bug'}, author={'name': 'X'},
                      updated_on='2024-01-01T00:00:00Z')
        mock_client.list_issues.return_value = [
            RedmineIssue(id=1, subject='Dated', start_date='2026-10-26', due_date='2026-11-01', **common),
            RedmineIssue(id=2, subject='Undated', **common),
        ]
        mock_get_client.return_value = mock_client

        lines = get_my_issues("open", 10).split('\n')
        dash = next(i for i, l in enumerate(lines) if l.startswith('-----'))
        widths = [len(seg) for seg in lines[dash].split(' ')]

        def cells(line):
            out, at = [], 0
            for i, w in enumerate(widths):
                end = len(line) if i == len(widths) - 1 else at + w
                assert i == len(widths) - 1 or end >= len(line) or line[end] == ' ', f'column {i} overflows: {line!r}'
                out.append(line[at:end].strip())
                at = end + 1
            return out

        header = cells(lines[dash - 1])
        dated = dict(zip(header, cells(lines[dash + 1])))
        undated = dict(zip(header, cells(lines[dash + 2])))
        assert header[-2:] == ['start', 'due']
        assert (dated['Update time'], dated['start'], dated['due']) == ('2024-01-01', '2026-10-26', '2026-11-01')
        assert (undated['start'], undated['due']) == ('', '')

    @patch('redmine_mcp.server.get_client')
    def test_get_my_issues_filters_by_status_names(self, mock_get_client):
        """statuses= resolves names to ids via get_issue_statuses; unknown names are skipped"""
        mock_client = Mock()
        mock_client.get_current_user.return_value = {'id': 1, 'firstname': 'T', 'lastname': 'U'}
        mock_client.get_issue_statuses.return_value = [
            {'id': 1, 'name': '新建立'}, {'id': 2, 'name': '實作中'}, {'id': 3, 'name': '已解決'},
        ]
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client

        get_my_issues(statuses='實作中,新建立,不存在')

        # Redmine REST status_id takes a single value, so each status is queried on its own
        calls = mock_client.list_issues.call_args_list
        assert [c.kwargs['status_id'] for c in calls] == [2, 1]  # resolved in order, unknown skipped

    @patch('redmine_mcp.server.get_client')
    def test_get_my_issues_header_shows_status_names(self, mock_get_client):
        """header line reflects the status names actually filtered by, not the open/closed flag"""
        mock_client = Mock()
        mock_client.get_current_user.return_value = {'id': 1, 'firstname': 'T', 'lastname': 'U'}
        mock_client.get_issue_statuses.return_value = [{'id': 2, 'name': '實作中'}]
        mock_client.list_issues.return_value = [RedmineIssue(
            id=1, subject='S', description=None, status={'name': '實作中'}, priority={'name': 'Normal'},
            project={'name': 'P', 'id': 1}, tracker={'name': 'Bug'}, author={'name': 'X'}, updated_on='2024-01-01T00:00:00Z')]
        mock_get_client.return_value = mock_client

        result = get_my_issues(statuses='實作中')
        assert 'Status filter: 實作中' in result

    @patch('redmine_mcp.server.get_client')
    def test_get_my_issues_merges_results_from_each_status(self, mock_get_client):
        """each status is queried separately; results merge, dedup, sort by updated desc, cap at limit"""
        mock_client = Mock()
        mock_client.get_current_user.return_value = {'id': 1, 'firstname': 'T', 'lastname': 'U'}
        mock_client.get_issue_statuses.return_value = [{'id': 1, 'name': '新建立'}, {'id': 2, 'name': '實作中'}]
        common = dict(description=None, priority={'name': 'Normal'}, project={'name': 'P', 'id': 1},
                      tracker={'name': 'Bug'}, author={'name': 'X'})
        impl = RedmineIssue(id=10, subject='impl', status={'name': '實作中'}, updated_on='2026-10-28T00:00:00Z', **common)
        newb = RedmineIssue(id=11, subject='new', status={'name': '新建立'}, updated_on='2026-10-29T00:00:00Z', **common)
        mock_client.list_issues.side_effect = lambda **kw: {2: [impl], 1: [newb]}[kw['status_id']]
        mock_get_client.return_value = mock_client

        result = get_my_issues(statuses='實作中,新建立', limit=5)

        assert 'Found 2 issues:' in result
        # 11 updated later than 10 → sorted first
        assert result.index('11') < result.index('10')

    @patch('redmine_mcp.server.get_client')
    def test_get_my_issues_status_names_all_unknown_falls_back_to_open(self, mock_get_client):
        """when no name resolves, fall back to the status_filter open behaviour"""
        mock_client = Mock()
        mock_client.get_current_user.return_value = {'id': 1, 'firstname': 'T', 'lastname': 'U'}
        mock_client.get_issue_statuses.return_value = [{'id': 1, 'name': '新建立'}]
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client

        get_my_issues(statuses='沒有這個狀態')

        _, kwargs = mock_client.list_issues.call_args
        assert kwargs['status_id'] == 'o'

    @patch('redmine_mcp.server.get_client')
    def test_get_my_issues_no_statuses_keeps_open_filter(self, mock_get_client):
        """statuses default empty: unchanged open behaviour, no get_issue_statuses call"""
        mock_client = Mock()
        mock_client.get_current_user.return_value = {'id': 1, 'firstname': 'T', 'lastname': 'U'}
        mock_client.list_issues.return_value = []
        mock_get_client.return_value = mock_client

        get_my_issues()

        _, kwargs = mock_client.list_issues.call_args
        assert kwargs['status_id'] == 'o'
        mock_client.get_issue_statuses.assert_not_called()

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


class TestAttachFilesToIssue:
    """attach_files_to_issue tool tests"""

    def setup_method(self):
        """Setup before each test"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }, clear=True), patch('redmine_mcp.config.load_dotenv'):
            pass

    @patch('redmine_mcp.server.get_client')
    def test_attach_files_success(self, mock_get_client, tmp_path):
        """Test attaching files without a note"""
        test_file = tmp_path / "log.txt"
        test_file.write_bytes(b"some log content")

        mock_client = Mock()
        mock_client.upload_files.return_value = [
            {'token': '1.aaa', 'filename': 'log.txt', 'content_type': 'text/plain'}
        ]
        mock_issue = Mock()
        mock_issue.subject = 'Test Issue'
        mock_client.get_issue.return_value = mock_issue
        mock_get_client.return_value = mock_client

        result = attach_files_to_issue(123, [str(test_file)])

        assert "Files attached successfully" in result
        assert "log.txt" in result
        mock_client.upload_files.assert_called_once_with([str(test_file)])
        mock_client.update_issue.assert_called_once_with(
            123,
            uploads=[{'token': '1.aaa', 'filename': 'log.txt', 'content_type': 'text/plain'}]
        )

    @patch('redmine_mcp.server.get_client')
    def test_attach_files_with_private_note(self, mock_get_client, tmp_path):
        """Test attaching files together with a private note"""
        test_file = tmp_path / "screenshot.png"
        test_file.write_bytes(b"\x89PNG fake")

        uploads = [{'token': '2.bbb', 'filename': 'screenshot.png', 'content_type': 'image/png'}]
        mock_client = Mock()
        mock_client.upload_files.return_value = uploads
        mock_issue = Mock()
        mock_issue.subject = 'Test Issue'
        mock_client.get_issue.return_value = mock_issue
        mock_get_client.return_value = mock_client

        result = attach_files_to_issue(123, [str(test_file)], notes="see screenshot", private=True)

        assert "Files attached successfully" in result
        assert "see screenshot" in result
        assert "private" in result
        mock_client.update_issue.assert_called_once_with(
            123, uploads=uploads, notes="see screenshot", private_notes=True
        )

    @patch('redmine_mcp.server.get_client')
    def test_attach_files_empty_list(self, mock_get_client):
        """Test empty file_paths is rejected"""
        result = attach_files_to_issue(123, [])

        assert "Error" in result
        mock_get_client.return_value.update_issue.assert_not_called()

    @patch('redmine_mcp.server.get_client')
    def test_attach_files_upload_failure_aborts(self, mock_get_client):
        """Test upload failure aborts without touching the issue"""
        mock_client = Mock()
        mock_client.upload_files.side_effect = RedmineAPIError(
            "File does not exist or is not a file: /no/such.txt"
        )
        mock_get_client.return_value = mock_client

        result = attach_files_to_issue(123, ['/no/such.txt'])

        assert "Failed to attach files" in result
        assert "/no/such.txt" in result
        mock_client.update_issue.assert_not_called()
