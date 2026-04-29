"""
Data validator tests
"""

import pytest
from redmine_mcp.validators import (
    RedmineValidator, RedmineValidationError, ValidationResult,
    validate_and_clean_data
)


class TestRedmineValidator:
    """RedmineValidator tests"""
    
    def test_validate_issue_data_success(self):
        """Test issue data validation success"""
        data = {
            'project_id': 1,
            'subject': 'Test Issue',
            'description': 'Test description',
            'tracker_id': 1,
            'status_id': 1,
            'priority_id': 2,
            'assigned_to_id': 3,
            'done_ratio': 50
        }
        
        result = RedmineValidator.validate_issue_data(data)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_issue_data_missing_required_fields(self):
        """Test issue data missing required fields"""
        data = {'description': 'Description only'}
        
        result = RedmineValidator.validate_issue_data(data)
        
        assert not result.is_valid
        assert "Project ID (project_id) is required" in result.errors
        assert "Issue subject (subject) is required" in result.errors
    
    def test_validate_issue_data_invalid_subject(self):
        """Test invalid issue subject"""
        # Empty subject
        data = {'project_id': 1, 'subject': ''}
        result = RedmineValidator.validate_issue_data(data)
        assert not result.is_valid
        assert "Issue subject cannot be empty" in result.errors
        
        # Subject too long
        data = {'project_id': 1, 'subject': 'x' * 300}
        result = RedmineValidator.validate_issue_data(data)
        assert not result.is_valid
        assert "Issue subject length cannot exceed 255 characters" in result.errors
        
        # Non-string type
        data = {'project_id': 1, 'subject': 123}
        result = RedmineValidator.validate_issue_data(data)
        assert not result.is_valid
        assert "Issue subject must be a string" in result.errors
    
    def test_validate_issue_data_invalid_ids(self):
        """Test invalid ID fields"""
        data = {
            'project_id': -1,
            'subject': 'Test',
            'tracker_id': 0,
            'assigned_to_id': 'invalid'
        }
        
        result = RedmineValidator.validate_issue_data(data)
        
        assert not result.is_valid
        assert "project_id must be a positive integer" in result.errors
        assert "tracker_id must be a positive integer" in result.errors
        assert "assigned_to_id must be a positive integer" in result.errors
    
    def test_validate_issue_data_invalid_done_ratio(self):
        """Test invalid done ratio"""
        data = {'project_id': 1, 'subject': 'Test', 'done_ratio': 150}
        
        result = RedmineValidator.validate_issue_data(data)
        
        assert not result.is_valid
        assert "Done ratio (done_ratio) must be an integer between 0-100" in result.errors
    
    def test_validate_issue_data_update_mode(self):
        """Test validation in update mode"""
        # Update mode does not require required fields
        data = {'subject': 'Updated title'}
        
        result = RedmineValidator.validate_issue_data(data, is_update=True)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_project_data_success(self):
        """Test project data validation success"""
        data = {
            'name': 'Test Project',
            'identifier': 'test-project',
            'description': 'Project description',
            'is_public': True,
            'inherit_members': False
        }
        
        result = RedmineValidator.validate_project_data(data)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_project_data_missing_required_fields(self):
        """Test project data missing required fields"""
        data = {'description': 'Description only'}
        
        result = RedmineValidator.validate_project_data(data)
        
        assert not result.is_valid
        assert "Project name (name) is required" in result.errors
        assert "Project identifier (identifier) is required" in result.errors
    
    def test_validate_project_data_invalid_identifier(self):
        """Test invalid project identifier"""
        # Contains uppercase letters
        data = {'name': 'Test', 'identifier': 'Test-Project'}
        result = RedmineValidator.validate_project_data(data)
        assert not result.is_valid
        assert "Project identifier can only contain lowercase letters, numbers, hyphens and underscores" in result.errors
        
        # Contains spaces
        data = {'name': 'Test', 'identifier': 'test project'}
        result = RedmineValidator.validate_project_data(data)
        assert not result.is_valid
        assert "Project identifier can only contain lowercase letters, numbers, hyphens and underscores" in result.errors
        
        # Too long
        data = {'name': 'Test', 'identifier': 'x' * 150}
        result = RedmineValidator.validate_project_data(data)
        assert not result.is_valid
        assert "Project identifier length cannot exceed 100 characters" in result.errors
    
    def test_validate_query_params_success(self):
        """Test query parameter validation success"""
        params = {
            'project_id': 1,
            'status_id': 2,
            'limit': 50,
            'offset': 0,
            'created_on': '2024-01-01',
            'sort': 'created_on:desc'
        }
        
        result = RedmineValidator.validate_query_params(params)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_query_params_invalid_pagination(self):
        """Test invalid pagination parameters"""
        params = {'limit': -1, 'offset': -5}
        
        result = RedmineValidator.validate_query_params(params)
        
        assert not result.is_valid
        assert "Pagination limit (limit) must be a positive integer" in result.errors
        assert "Pagination offset (offset) must be a non-negative integer" in result.errors
    
    def test_validate_query_params_date_formats(self):
        """Test date format validation"""
        # Valid formats
        valid_dates = [
            '2024-01-01',
            '>=2024-01-01',
            '<=2024-12-31',
            '2024-01-01|2024-12-31',
            '2024-01-01T10:30:00Z'
        ]
        
        for date in valid_dates:
            params = {'created_on': date}
            result = RedmineValidator.validate_query_params(params)
            assert result.is_valid, f"Date format {date} should be valid"
        
        # Invalid formats
        invalid_dates = ['2024/01/01', 'invalid-date', '2024-13-01']
        
        for date in invalid_dates:
            params = {'created_on': date}
            result = RedmineValidator.validate_query_params(params)
            assert not result.is_valid, f"Date format {date} should be invalid"
    
    def test_get_friendly_error_message(self):
        """Test friendly error message conversion"""
        # Test 401 error
        error = Exception("HTTP 401 Unauthorized")
        message = RedmineValidator.get_friendly_error_message(error)
        assert "Authentication failed" in message
        
        # Test 404 error related to issue
        error = Exception("HTTP 404 Not Found")
        message = RedmineValidator.get_friendly_error_message(error, "issue")
        assert "The specified issue was not found" in message
        
        # Test connection error
        error = Exception("Connection failed")
        message = RedmineValidator.get_friendly_error_message(error)
        assert "Connection failed" in message


class TestValidateAndCleanData:
    """Test data validation and cleaning function"""
    
    def test_validate_and_clean_issue_data_success(self):
        """Test issue data validation and cleaning success"""
        data = {
            'project_id': 1,
            'subject': 'Test Issue',
            'description': '',  # Empty string should be removed
            'tracker_id': None,  # None value should be removed
            'status_id': 1
        }
        
        cleaned = validate_and_clean_data(data, "issue")
        
        assert 'project_id' in cleaned
        assert 'subject' in cleaned
        assert 'status_id' in cleaned
        assert 'description' not in cleaned  # Empty string removed
        assert 'tracker_id' not in cleaned   # None value removed
    
    def test_validate_and_clean_data_validation_error(self):
        """Test error raised when validation fails"""
        data = {'subject': ''}  # Missing required fields
        
        with pytest.raises(RedmineValidationError) as exc_info:
            validate_and_clean_data(data, "issue")
        
        assert "Data validation failed" in str(exc_info.value)
        assert len(exc_info.value.errors) > 0
    
    def test_validate_and_clean_data_invalid_type(self):
        """Test invalid validation type"""
        data = {'test': 'data'}
        
        with pytest.raises(ValueError, match="Unsupported validation type"):
            validate_and_clean_data(data, "invalid_type")
