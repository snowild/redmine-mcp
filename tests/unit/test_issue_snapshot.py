"""
Test issue snapshot mechanism
"""
import pytest
from unittest.mock import patch, MagicMock
from redmine_mcp.redmine_client import RedmineClient


@pytest.fixture
def mock_client():
    """Create a mock RedmineClient"""
    with patch.object(RedmineClient, '__init__', lambda self: None):
        client = RedmineClient()
        client._issue_snapshots = {}
        client.config = MagicMock()
        client.config.redmine_domain = "https://test.redmine.com"
        client.session = MagicMock()
        return client


class TestIssueSnapshotInit:
    def test_starts_empty(self, mock_client):
        assert mock_client._issue_snapshots == {}


class TestSaveIssueSnapshot:
    def test_saves_basic_fields(self, mock_client):
        issue_data = {
            'id': 123,
            'subject': 'Test Issue',
            'description': 'Description content',
            'status': {'id': 2, 'name': 'In Progress'},
            'priority': {'id': 6, 'name': 'Normal'},
            'assigned_to': {'id': 1, 'name': 'John Doe'},
            'done_ratio': 50,
            'updated_on': '2026-03-07T10:00:00Z',
            'journals': [
                {'id': 1, 'notes': 'Note 1'},
                {'id': 2, 'notes': 'Note 2'},
            ],
            'attachments': [
                {'id': 10, 'filename': 'test.pdf'},
            ],
            'custom_fields': [
                {'id': 23, 'name': 'Actual End Date', 'value': '2026-03-07'},
            ],
        }

        mock_client._save_issue_snapshot(123, issue_data)

        snapshot = mock_client._issue_snapshots[123]
        assert snapshot['status'] == 'In Progress'
        assert snapshot['status_id'] == 2
        assert snapshot['priority'] == 'Normal'
        assert snapshot['assigned_to'] == 'John Doe'
        assert snapshot['done_ratio'] == 50
        assert snapshot['subject'] == 'Test Issue'
        assert snapshot['description'] == 'Description content'
        assert snapshot['journals_count'] == 2
        assert snapshot['last_journal_id'] == 2
        assert snapshot['attachments_count'] == 1
        assert snapshot['custom_fields'] == {23: '2026-03-07'}
        assert 'snapshot_time' in snapshot

    def test_handles_no_assigned_to(self, mock_client):
        issue_data = {
            'id': 124,
            'subject': 'Unassigned',
            'description': '',
            'status': {'id': 1, 'name': 'New'},
            'priority': {'id': 6, 'name': 'Normal'},
            'done_ratio': 0,
            'updated_on': '2026-03-07T10:00:00Z',
        }

        mock_client._save_issue_snapshot(124, issue_data)
        snapshot = mock_client._issue_snapshots[124]
        assert snapshot['assigned_to'] is None
        assert snapshot['journals_count'] == 0
        assert snapshot['last_journal_id'] is None
        assert snapshot['attachments_count'] == 0

    def test_overwrites_previous_snapshot(self, mock_client):
        issue_v1 = {
            'id': 125,
            'subject': 'v1',
            'description': '',
            'status': {'id': 1, 'name': 'New'},
            'priority': {'id': 6, 'name': 'Normal'},
            'done_ratio': 0,
            'updated_on': '2026-03-07T10:00:00Z',
        }
        issue_v2 = {
            'id': 125,
            'subject': 'v2',
            'description': '',
            'status': {'id': 2, 'name': 'In Progress'},
            'priority': {'id': 6, 'name': 'Normal'},
            'done_ratio': 30,
            'updated_on': '2026-03-07T12:00:00Z',
        }

        mock_client._save_issue_snapshot(125, issue_v1)
        mock_client._save_issue_snapshot(125, issue_v2)

        snapshot = mock_client._issue_snapshots[125]
        assert snapshot['subject'] == 'v2'
        assert snapshot['status'] == 'In Progress'
        assert snapshot['done_ratio'] == 30


class TestGetIssueSnapshot:
    def test_returns_snapshot(self, mock_client):
        mock_client._issue_snapshots[123] = {'status': 'In Progress'}
        assert mock_client.get_issue_snapshot(123) == {'status': 'In Progress'}

    def test_returns_none_if_not_found(self, mock_client):
        assert mock_client.get_issue_snapshot(999) is None


class TestClearIssueSnapshot:
    def test_clears_existing(self, mock_client):
        mock_client._issue_snapshots[123] = {'status': 'In Progress'}
        mock_client.clear_issue_snapshot(123)
        assert 123 not in mock_client._issue_snapshots

    def test_no_error_if_not_exists(self, mock_client):
        mock_client.clear_issue_snapshot(999)  # Should not raise an exception
