"""
Data validation and error feedback mechanism
Responsible for validating API request parameters and providing user-friendly error messages
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Validation result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class RedmineValidationError(Exception):
    """Redmine data validation error"""
    def __init__(self, message: str, field: str = None, errors: List[str] = None):
        super().__init__(message)
        self.field = field
        self.errors = errors or [message]


class RedmineValidator:
    """Redmine data validator"""

    # Validation rule constants
    MAX_SUBJECT_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 65535
    MAX_PROJECT_NAME_LENGTH = 255
    MAX_PROJECT_IDENTIFIER_LENGTH = 100
    MIN_PROJECT_IDENTIFIER_LENGTH = 1

    # Project identifier format: lowercase letters, numbers, hyphens and underscores only
    PROJECT_IDENTIFIER_PATTERN = re.compile(r'^[a-z0-9\-_]+$')

    # Date formats: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ
    DATE_PATTERNS = [
        re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'),  # YYYY-MM-DD (with validation)
        re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T\d{2}:\d{2}:\d{2}Z?$'),  # ISO format
        re.compile(r'^>=\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'),  # >=YYYY-MM-DD
        re.compile(r'^<=\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'),  # <=YYYY-MM-DD
        re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\|\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$')  # date range
    ]

    @classmethod
    def validate_issue_data(cls, data: Dict[str, Any], is_update: bool = False) -> ValidationResult:
        """Validate issue data"""
        errors = []
        warnings = []

        # Required field check (on create)
        if not is_update:
            if 'project_id' not in data:
                errors.append("Project ID (project_id) is required")
            if 'subject' not in data:
                errors.append("Issue subject (subject) is required")
            elif not isinstance(data.get('subject'), str) or not data.get('subject', '').strip():
                errors.append("Issue subject (subject) is required")

        # Issue subject validation
        if 'subject' in data:
            subject = data['subject']
            if not isinstance(subject, str):
                errors.append("Issue subject must be a string")
            elif len(subject.strip()) == 0:
                errors.append("Issue subject cannot be empty")
            elif len(subject) > cls.MAX_SUBJECT_LENGTH:
                errors.append(f"Issue subject length cannot exceed {cls.MAX_SUBJECT_LENGTH} characters")

        # Issue description validation
        if 'description' in data:
            description = data['description']
            if description is not None and not isinstance(description, str):
                errors.append("Issue description must be a string")
            elif description and len(description) > cls.MAX_DESCRIPTION_LENGTH:
                errors.append(f"Issue description length cannot exceed {cls.MAX_DESCRIPTION_LENGTH} characters")

        # ID field validation
        id_fields = ['project_id', 'tracker_id', 'status_id', 'priority_id', 'assigned_to_id', 'parent_issue_id']
        for field in id_fields:
            if field in data:
                value = data[field]
                if value is not None and (not isinstance(value, int) or value <= 0):
                    errors.append(f"{field} must be a positive integer")

        # Done ratio validation
        if 'done_ratio' in data:
            done_ratio = data['done_ratio']
            if not isinstance(done_ratio, int) or done_ratio < 0 or done_ratio > 100:
                errors.append("Done ratio (done_ratio) must be an integer between 0-100")

        # Custom fields validation
        if 'custom_fields' in data:
            custom_fields = data['custom_fields']
            if custom_fields is not None:  # Only validate if not None
                if not isinstance(custom_fields, list):
                    errors.append("Custom fields (custom_fields) must be an array")
                else:
                    for i, field in enumerate(custom_fields):
                        if not isinstance(field, dict):
                            errors.append(f"Custom field [{i}] must be an object")
                        elif 'id' not in field:
                            errors.append(f"Custom field [{i}] is missing the required id field")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    @classmethod
    def validate_project_data(cls, data: Dict[str, Any], is_update: bool = False) -> ValidationResult:
        """Validate project data"""
        errors = []
        warnings = []

        # Required field check (on create)
        if not is_update:
            if 'name' not in data or not data.get('name', '').strip():
                errors.append("Project name (name) is required")
            if 'identifier' not in data or not data.get('identifier', '').strip():
                errors.append("Project identifier (identifier) is required")

        # Project name validation
        if 'name' in data:
            name = data['name']
            if not isinstance(name, str):
                errors.append("Project name must be a string")
            elif len(name.strip()) == 0:
                errors.append("Project name cannot be empty")
            elif len(name) > cls.MAX_PROJECT_NAME_LENGTH:
                errors.append(f"Project name length cannot exceed {cls.MAX_PROJECT_NAME_LENGTH} characters")

        # Project identifier validation
        if 'identifier' in data:
            identifier = data['identifier']
            if not isinstance(identifier, str):
                errors.append("Project identifier must be a string")
            elif len(identifier.strip()) == 0:
                errors.append("Project identifier cannot be empty")
            elif len(identifier) < cls.MIN_PROJECT_IDENTIFIER_LENGTH:
                errors.append(f"Project identifier length cannot be less than {cls.MIN_PROJECT_IDENTIFIER_LENGTH} characters")
            elif len(identifier) > cls.MAX_PROJECT_IDENTIFIER_LENGTH:
                errors.append(f"Project identifier length cannot exceed {cls.MAX_PROJECT_IDENTIFIER_LENGTH} characters")
            elif not cls.PROJECT_IDENTIFIER_PATTERN.match(identifier):
                errors.append("Project identifier can only contain lowercase letters, numbers, hyphens and underscores")
            elif identifier.lower() != identifier:
                warnings.append("It is recommended to use lowercase letters for the project identifier")

        # Project description validation
        if 'description' in data:
            description = data['description']
            if description is not None and not isinstance(description, str):
                errors.append("Project description must be a string")

        # Boolean field validation
        bool_fields = ['is_public', 'inherit_members']
        for field in bool_fields:
            if field in data:
                value = data[field]
                if not isinstance(value, bool):
                    errors.append(f"{field} must be a boolean (true/false)")

        # ID field validation
        if 'parent_id' in data:
            parent_id = data['parent_id']
            if parent_id is not None and (not isinstance(parent_id, int) or parent_id <= 0):
                errors.append("Parent project ID (parent_id) must be a positive integer")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    @classmethod
    def validate_query_params(cls, params: Dict[str, Any]) -> ValidationResult:
        """Validate query parameters"""
        errors = []
        warnings = []

        # Pagination parameter validation
        if 'limit' in params:
            limit = params['limit']
            if not isinstance(limit, int) or limit <= 0:
                errors.append("Pagination limit (limit) must be a positive integer")
            elif limit > 100:
                warnings.append("It is recommended to keep pagination limit at or below 100 for performance")

        if 'offset' in params:
            offset = params['offset']
            if not isinstance(offset, int) or offset < 0:
                errors.append("Pagination offset (offset) must be a non-negative integer")

        # ID filter parameter validation
        id_fields = ['project_id', 'tracker_id', 'priority_id', 'assigned_to_id', 'author_id']
        for field in id_fields:
            if field in params:
                value = params[field]
                if value is not None and (not isinstance(value, int) or value <= 0):
                    errors.append(f"{field} must be a positive integer")

        # Special handling for status_id (supports Redmine special values)
        if 'status_id' in params:
            status_id = params['status_id']
            if status_id is not None:
                # Allow positive integers or Redmine special values ('o' for open, 'c' for closed)
                if not (isinstance(status_id, int) and status_id > 0) and status_id not in ['o', 'c']:
                    errors.append("status_id must be a positive integer or 'o' (open)/'c' (closed)")

        # Date filter parameter validation
        date_fields = ['created_on', 'updated_on']
        for field in date_fields:
            if field in params:
                date_value = params[field]
                if date_value and not cls._is_valid_date_filter(date_value):
                    errors.append(f"{field} has an invalid date format. Supported formats: YYYY-MM-DD, >=YYYY-MM-DD, <=YYYY-MM-DD")

        # Sort parameter validation
        if 'sort' in params:
            sort_value = params['sort']
            if sort_value is not None and not isinstance(sort_value, str):
                errors.append("Sort parameter (sort) must be a string")
            elif sort_value and not cls._is_valid_sort_field(sort_value):
                warnings.append(f"Sort field '{sort_value}' may not be supported")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    @classmethod
    def _is_valid_date_filter(cls, date_str: str) -> bool:
        """Validate date filter format"""
        if not isinstance(date_str, str):
            return False

        return any(pattern.match(date_str) for pattern in cls.DATE_PATTERNS)

    @classmethod
    def _is_valid_sort_field(cls, sort_str: str) -> bool:
        """Validate sort field"""
        # Remove :desc or :asc suffix
        field = sort_str.split(':')[0]

        # Common sort fields
        valid_fields = [
            'id', 'subject', 'status', 'priority', 'author', 'assigned_to',
            'created_on', 'updated_on', 'due_date', 'done_ratio', 'project'
        ]

        return field in valid_fields

    @classmethod
    def get_friendly_error_message(cls, error: Exception, context: str = "") -> str:
        """Convert technical errors into user-friendly error messages"""
        error_msg = str(error).lower()

        # HTTP error message conversion
        if "401" in error_msg or "unauthorized" in error_msg:
            return "Authentication failed: please check if your API key is correct"
        elif "403" in error_msg or "forbidden" in error_msg:
            return "Insufficient permissions: you do not have permission to perform this operation"
        elif "404" in error_msg or "not found" in error_msg:
            if "issue" in context.lower():
                return "The specified issue was not found, please verify the issue ID is correct"
            elif "project" in context.lower():
                return "The specified project was not found, please verify the project ID or identifier is correct"
            else:
                return "The specified resource was not found"
        elif "422" in error_msg or "unprocessable" in error_msg:
            return "Data format error: please check if the input data meets the requirements"
        elif "500" in error_msg or "internal server error" in error_msg:
            return "Internal server error: please try again later or contact the system administrator"
        elif "timeout" in error_msg:
            return "Request timed out: the network connection may be unstable, please try again later"
        elif "connection" in error_msg or "connectionerror" in error_msg:
            return "Connection failed: please check your network connection and Redmine server status"
        elif "httperror" in error_msg:
            return f"HTTP error: {str(error)}"

        # Other common errors
        if "json" in error_msg and "decode" in error_msg:
            return "Response format error: the server returned data in an incorrect format"

        # Default error message
        return f"Operation failed: {str(error)}"


def validate_and_clean_data(data: Dict[str, Any], validation_type: str) -> Dict[str, Any]:
    """Validate and clean data"""
    if validation_type == "issue":
        result = RedmineValidator.validate_issue_data(data)
    elif validation_type == "project":
        result = RedmineValidator.validate_project_data(data)
    elif validation_type == "query":
        result = RedmineValidator.validate_query_params(data)
    else:
        raise ValueError(f"Unsupported validation type: {validation_type}")

    if not result.is_valid:
        raise RedmineValidationError(
            f"Data validation failed: {'; '.join(result.errors)}",
            errors=result.errors
        )

    # Return cleaned data (remove None values and empty strings)
    cleaned_data = {}
    for key, value in data.items():
        if value is not None and value != "":
            cleaned_data[key] = value

    return cleaned_data
