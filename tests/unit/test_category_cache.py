"""
Test on-demand category cache mechanism for issues
"""
import pytest
from unittest.mock import patch, MagicMock
from redmine_mcp.redmine_client import RedmineClient


@pytest.fixture
def mock_client():
    """Create a mock RedmineClient"""
    with patch.object(RedmineClient, '__init__', lambda self: None):
        client = RedmineClient()
        client._category_cache = {}
        client.config = MagicMock()
        client.config.redmine_domain = "https://test.redmine.com"
        client.session = MagicMock()
        return client


class TestCategoryCacheInit:
    def test_category_cache_starts_empty(self, mock_client):
        assert mock_client._category_cache == {}


class TestLoadCategoryCache:
    def test_first_load_calls_api(self, mock_client):
        mock_client.get_issue_categories = MagicMock(return_value=[
            {'id': 521, 'name': 'Frontend'},
            {'id': 522, 'name': 'Backend'},
        ])

        result = mock_client._load_category_cache(1)

        mock_client.get_issue_categories.assert_called_once_with(1)
        assert result == {'Frontend': 521, 'Backend': 522}

    def test_second_load_uses_cache(self, mock_client):
        mock_client.get_issue_categories = MagicMock(return_value=[
            {'id': 521, 'name': 'Frontend'},
        ])

        mock_client._load_category_cache(1)
        mock_client._load_category_cache(1)

        # API called only once
        mock_client.get_issue_categories.assert_called_once()

    def test_different_projects_separate_cache(self, mock_client):
        mock_client.get_issue_categories = MagicMock(side_effect=[
            [{'id': 521, 'name': 'Frontend'}],
            [{'id': 600, 'name': 'Design'}],
        ])

        result1 = mock_client._load_category_cache(1)
        result2 = mock_client._load_category_cache(2)

        assert result1 == {'Frontend': 521}
        assert result2 == {'Design': 600}
        assert mock_client.get_issue_categories.call_count == 2

    def test_api_failure_returns_empty(self, mock_client):
        mock_client.get_issue_categories = MagicMock(side_effect=Exception("API error"))

        result = mock_client._load_category_cache(1)
        assert result == {}


class TestFindCategoryIdByName:
    def test_find_existing(self, mock_client):
        mock_client._category_cache = {1: {'Frontend': 521, 'Backend': 522}}
        assert mock_client.find_category_id_by_name(1, 'Frontend') == 521

    def test_find_nonexistent(self, mock_client):
        mock_client._category_cache = {1: {'Frontend': 521}}
        assert mock_client.find_category_id_by_name(1, 'QA') is None


class TestGetAvailableCategories:
    def test_returns_cached_categories(self, mock_client):
        mock_client._category_cache = {1: {'Frontend': 521, 'Backend': 522}}
        result = mock_client.get_available_categories(1)
        assert result == {'Frontend': 521, 'Backend': 522}


class TestRefreshCategoryCache:
    def test_refresh_clears_and_reloads(self, mock_client):
        mock_client._category_cache = {1: {'Frontend': 521}}
        mock_client.get_issue_categories = MagicMock(return_value=[
            {'id': 521, 'name': 'Frontend'},
            {'id': 523, 'name': 'Devops'},
        ])

        mock_client.refresh_category_cache(1)

        assert mock_client._category_cache[1] == {'Frontend': 521, 'Devops': 523}

    def test_refresh_only_affects_target_project(self, mock_client):
        mock_client._category_cache = {1: {'Frontend': 521}, 2: {'Design': 600}}
        mock_client.get_issue_categories = MagicMock(return_value=[
            {'id': 521, 'name': 'Frontend Updated'},
        ])

        mock_client.refresh_category_cache(1)

        assert mock_client._category_cache[1] == {'Frontend Updated': 521}
        assert mock_client._category_cache[2] == {'Design': 600}  # Not affected
