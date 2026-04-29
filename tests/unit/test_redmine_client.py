"""
Redmine client tests
"""

import os
import pytest
from unittest.mock import patch, Mock
import requests
from redmine_mcp.redmine_client import (
    RedmineClient, RedmineAPIError, RedmineIssue, RedmineProject,
    get_client, reload_client
)


class TestRedmineClient:
    """RedmineClient class tests"""
    
    def setup_method(self):
        """Setup before each test"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            self.client = RedmineClient()
    
    def test_client_initialization(self):
        """Test client initialization"""
        assert self.client.config.redmine_domain == 'https://test.redmine.com'
        assert self.client.session.headers['X-Redmine-API-Key'] == 'test_api_key'
        assert self.client.session.timeout == 30
    
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.content = b'{"test": "data"}'
        mock_request.return_value = mock_response
        
        result = self.client._make_request('GET', '/test')
        
        assert result == {'test': 'data'}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_make_request_timeout(self, mock_request):
        """Test request timeout"""
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(RedmineAPIError, match="Request timed out"):
            self.client._make_request('GET', '/test')
    
    @patch('requests.Session.request')
    def test_make_request_connection_error(self, mock_request):
        """Test connection error"""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(RedmineAPIError, match="Connection failed"):
            self.client._make_request('GET', '/test')
    
    @patch('requests.Session.request')
    def test_make_request_http_error(self, mock_request):
        """Test HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'errors': ['Not found']}
        mock_response.content = b'{"errors": ["Not found"]}'
        
        mock_http_error = requests.exceptions.HTTPError("HTTP 404 Not Found")
        mock_http_error.response = mock_response
        mock_response.raise_for_status.side_effect = mock_http_error
        mock_request.return_value = mock_response
        
        with pytest.raises(RedmineAPIError, match="not found"):
            self.client._make_request('GET', '/test')
    
    @patch('requests.Session.request')
    def test_get_issue_success(self, mock_request):
        """Test successful issue retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'issue': {
                'id': 1,
                'subject': 'Test Issue',
                'description': 'Test description',
                'status': {'id': 1, 'name': 'New'},
                'priority': {'id': 2, 'name': 'Normal'},
                'project': {'id': 1, 'name': 'Test Project'},
                'tracker': {'id': 1, 'name': 'Bug'},
                'author': {'id': 1, 'name': 'Test User'},
                'done_ratio': 0
            }
        }
        mock_response.content = b'content'
        mock_request.return_value = mock_response
        
        issue = self.client.get_issue(1)
        
        assert isinstance(issue, RedmineIssue)
        assert issue.id == 1
        assert issue.subject == 'Test Issue'
        assert issue.status['name'] == 'New'
    
    @patch('requests.Session.request')
    def test_get_issue_not_found(self, mock_request):
        """Test issue not found"""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.content = b'{}'
        mock_request.return_value = mock_response
        
        with pytest.raises(RedmineAPIError, match="Issue 1 does not exist"):
            self.client.get_issue(1)
    
    @patch('requests.Session.request')
    def test_list_issues_success(self, mock_request):
        """Test listing issues"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'issues': [
                {
                    'id': 1,
                    'subject': 'Issue1',
                    'description': 'Description1',
                    'status': {'id': 1, 'name': 'New'},
                    'priority': {'id': 2, 'name': 'Normal'},
                    'project': {'id': 1, 'name': 'Project1'},
                    'tracker': {'id': 1, 'name': 'Bug'},
                    'author': {'id': 1, 'name': 'User1'}
                },
                {
                    'id': 2,
                    'subject': 'Issue2',
                    'description': 'Description2',
                    'status': {'id': 2, 'name': 'In Progress'},
                    'priority': {'id': 3, 'name': 'High'},
                    'project': {'id': 1, 'name': 'Project1'},
                    'tracker': {'id': 2, 'name': 'Feature'},
                    'author': {'id': 2, 'name': 'User2'}
                }
            ]
        }
        mock_response.content = b'content'
        mock_request.return_value = mock_response
        
        issues = self.client.list_issues()
        
        assert len(issues) == 2
        assert all(isinstance(issue, RedmineIssue) for issue in issues)
        assert issues[0].subject == 'Issue1'
        assert issues[1].subject == 'Issue2'
    
    @patch('requests.Session.request')
    def test_update_issue_success(self, mock_request):
        """Test updating issue"""
        mock_response = Mock()
        mock_response.content = b''
        mock_request.return_value = mock_response
        
        result = self.client.update_issue(1, subject='New Title', status_id=2)
        
        assert result is True
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]['json']['issue']['subject'] == 'New Title'
        assert call_args[1]['json']['issue']['status_id'] == 2
    
    def test_update_issue_no_fields(self):
        """Test updating issue without providing fields"""
        with pytest.raises(RedmineAPIError, match="No fields provided for update"):
            self.client.update_issue(1)
    
    @patch('requests.Session.request')
    def test_get_project_success(self, mock_request):
        """Test getting project"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'project': {
                'id': 1,
                'name': 'Test Project',
                'identifier': 'test-project',
                'description': 'Project description',
                'status': 1
            }
        }
        mock_response.content = b'content'
        mock_request.return_value = mock_response
        
        project = self.client.get_project(1)
        
        assert isinstance(project, RedmineProject)
        assert project.id == 1
        assert project.name == 'Test Project'
        assert project.identifier == 'test-project'
    
    @patch('requests.Session.request')
    def test_test_connection_success(self, mock_request):
        """Test successful connection"""
        mock_response = Mock()
        mock_response.json.return_value = {'user': {'id': 1, 'login': 'test'}}
        mock_response.content = b'content'
        mock_request.return_value = mock_response
        
        result = self.client.test_connection()
        
        assert result is True
    
    @patch('requests.Session.request')
    def test_test_connection_failure(self, mock_request):
        """Test connection failure"""
        mock_request.side_effect = RedmineAPIError("Connection failed")
        
        result = self.client.test_connection()
        
        assert result is False


class TestClientSingleton:
    """Test client singleton pattern"""
    
    def test_get_client_singleton(self):
        """Test get_client returns the same instance"""
        reload_client()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            client1 = get_client()
            client2 = get_client()
            
            assert client1 is client2
    
    def test_reload_client(self):
        """Test reload_client creates a new instance"""
        reload_client()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            client1 = get_client()
            client2 = reload_client()
            
            assert client1 is not client2
            assert client1.config.redmine_domain == client2.config.redmine_domain
