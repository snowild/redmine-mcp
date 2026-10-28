"""
Redmine returns null (not "") for empty text fields such as an issue's
description or a journal's notes. `.get(key, '')` only defaults a missing key,
so a present-but-null value reached `.strip()` and raised
"'NoneType' object has no attribute 'strip'".
"""
import pytest
from unittest.mock import patch, MagicMock

from redmine_mcp import server
from redmine_mcp.validators import RedmineValidator


def _issue(**overrides):
    data = {
        'id': 114111,
        'subject': 'Test issue',
        'description': None,
        'tracker': {'name': 'Bug'},
        'status': {'name': 'New'},
        'priority': {'name': 'Normal'},
        'project': {'id': 1, 'name': 'Demo'},
        'author': {'name': 'Someone'},
        'journals': [
            {'id': 1, 'user': {'name': 'A'}, 'created_on': '2026-10-28', 'notes': None, 'details': [{'name': 'status_id'}]},
            {'id': 2, 'user': {'name': 'B'}, 'created_on': '2026-10-28', 'notes': 'real note', 'details': []},
        ],
    }
    data.update(overrides)
    return data


@pytest.fixture
def client():
    mock = MagicMock()
    with patch.object(server, 'get_client', return_value=mock):
        yield mock


class TestGetIssueNullFields:
    @pytest.mark.parametrize('include_details', [False, True])
    def test_null_description(self, client, include_details):
        client.get_issue_raw.return_value = _issue()
        result = server.get_issue(114111, include_details=include_details)
        assert 'System error' not in result
        assert '(no description)' in result

    def test_null_journal_notes_are_skipped(self, client):
        client.get_issue_raw.return_value = _issue()
        result = server.get_issue(114111, include_details=True)
        assert 'System error' not in result
        assert 'real note' in result
        assert '(1 Pen)' in result


class TestJournalToolsNullNotes:
    def test_list_issue_journals(self, client):
        client.get_issue_journals.return_value = _issue()['journals']
        result = server.list_issue_journals(114111)
        assert 'System error' not in result
        assert 'real note' in result

    def test_list_issue_journals_with_property_changes(self, client):
        client.get_issue_journals.return_value = _issue()['journals']
        result = server.list_issue_journals(114111, include_property_changes=True)
        assert 'System error' not in result

    def test_get_journal_with_null_notes(self, client):
        client.get_issue_journals.return_value = _issue()['journals']
        result = server.get_journal(114111, 1)
        assert 'System error' not in result


class TestCheckIssueChangesNullNotes:
    def test_new_journal_with_null_notes(self, client):
        client.get_issue_snapshot.return_value = {
            'status': 'New', 'priority': 'Normal', 'assigned_to': None, 'done_ratio': 0,
            'subject': 'Test issue', 'description': None, 'journals_count': 0, 'attachments_count': 0,
            'updated_on': '2026-10-27',
        }
        client.get_issue_raw.return_value = _issue(attachments=[], updated_on='2026-10-28')
        result = server.check_issue_changes(114111)
        assert 'System error' not in result
        assert 'real note' in result


class TestValidateProjectNullFields:
    def test_null_name_and_identifier_are_errors_not_exceptions(self):
        result = RedmineValidator.validate_project_data({'name': None, 'identifier': None})
        assert not result.is_valid
        assert any('name' in e for e in result.errors)
        assert any('identifier' in e for e in result.errors)
