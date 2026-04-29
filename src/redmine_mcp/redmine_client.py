"""
Redmine API client
Responsible for HTTP communication with the Redmine system
"""

import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path

from .config import get_config
from .validators import RedmineValidator, validate_and_clean_data, RedmineValidationError


@dataclass
class RedmineIssue:
    """Redmine issue data structure"""
    id: int
    subject: str
    description: str
    status: Dict[str, Any]
    priority: Dict[str, Any]
    project: Dict[str, Any]
    tracker: Dict[str, Any]
    author: Dict[str, Any]
    assigned_to: Optional[Dict[str, Any]] = None
    created_on: Optional[str] = None
    updated_on: Optional[str] = None
    done_ratio: int = 0


@dataclass
class RedmineProject:
    """Redmine project data structure"""
    id: int
    name: str
    identifier: str
    description: str
    status: int
    created_on: Optional[str] = None
    updated_on: Optional[str] = None


@dataclass
class RedmineUser:
    """Redmine user data structure"""
    id: int
    login: str
    firstname: str
    lastname: str
    mail: str
    status: int
    created_on: Optional[str] = None
    last_login_on: Optional[str] = None


class RedmineAPIError(Exception):
    """Redmine API error"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RedmineClient:
    """Redmine API client"""
    
    def __init__(self):
        self.config = get_config()
        self.session = requests.Session()
        self.session.headers.update(self.config.api_headers)
        self.session.timeout = self.config.redmine_timeout
        
        # Cache-related settings
        self.cache_dir = Path.home() / ".redmine_mcp"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Create a unique cache file name based on domain
        domain_hash = hash(self.config.redmine_domain)
        safe_domain = self.config.redmine_domain.replace('://', '_').replace('/', '_').replace(':', '_')
        self._cache_file = self.cache_dir / f"cache_{safe_domain}_{abs(domain_hash)}.json"
        self._enum_cache: Optional[Dict[str, Any]] = None
        self._category_cache: Dict[int, Dict[str, int]] = {}  # {project_id: {name: id}}
        self._issue_snapshots: Dict[int, Dict[str, Any]] = {}  # {issue_id: snapshot}
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute HTTP request"""
        url = f"{self.config.redmine_domain}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.Timeout:
            friendly_msg = RedmineValidator.get_friendly_error_message(
                Exception("timeout"), "request"
            )
            raise RedmineAPIError(friendly_msg)
        except requests.exceptions.ConnectionError as e:
            friendly_msg = RedmineValidator.get_friendly_error_message(e, "connection")
            raise RedmineAPIError(friendly_msg)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            error_data = None
            try:
                if e.response and e.response.content:
                    error_data = e.response.json()
            except:
                pass
            
            # Use friendly error messages
            context = "issue" if "/issues" in url else "project" if "/projects" in url else "request"
            friendly_msg = RedmineValidator.get_friendly_error_message(e, context)
            raise RedmineAPIError(friendly_msg, status_code, error_data)
        except requests.exceptions.RequestException as e:
            friendly_msg = RedmineValidator.get_friendly_error_message(e, "request")
            raise RedmineAPIError(friendly_msg)
        except json.JSONDecodeError as e:
            friendly_msg = RedmineValidator.get_friendly_error_message(e, "response")
            raise RedmineAPIError(friendly_msg)
    
    def get_issue(self, issue_id: int, include: Optional[List[str]] = None) -> RedmineIssue:
        """Get a single issue"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        
        response = self._make_request('GET', f'/issues/{issue_id}.json', params=params)
        
        if 'issue' not in response:
            raise RedmineAPIError(f"Issue {issue_id} does not exist")
        
        issue_data = response['issue']
        return RedmineIssue(
            id=issue_data['id'],
            subject=issue_data['subject'],
            description=issue_data.get('description', ''),
            status=issue_data['status'],
            priority=issue_data['priority'],
            project=issue_data['project'],
            tracker=issue_data['tracker'],
            author=issue_data['author'],
            assigned_to=issue_data.get('assigned_to'),
            created_on=issue_data.get('created_on'),
            updated_on=issue_data.get('updated_on'),
            done_ratio=issue_data.get('done_ratio', 0)
        )
    
    def get_issue_raw(self, issue_id: int, include: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get raw API data for a single issue (including journals and attachments)"""
        params = {}
        if include:
            params['include'] = ','.join(include)

        response = self._make_request('GET', f'/issues/{issue_id}.json', params=params)

        if 'issue' not in response:
            raise RedmineAPIError(f"Issue {issue_id} does not exist")

        issue_data = response['issue']
        self._save_issue_snapshot(issue_id, issue_data)
        return issue_data

    def _save_issue_snapshot(self, issue_id: int, issue_data: Dict[str, Any]):
        """Save issue snapshot (for change detection)"""
        journals = issue_data.get('journals', [])
        attachments = issue_data.get('attachments', [])
        self._issue_snapshots[issue_id] = {
            'snapshot_time': datetime.now().isoformat(),
            'updated_on': issue_data.get('updated_on'),
            'status': issue_data.get('status', {}).get('name'),
            'status_id': issue_data.get('status', {}).get('id'),
            'priority': issue_data.get('priority', {}).get('name'),
            'assigned_to': issue_data.get('assigned_to', {}).get('name') if issue_data.get('assigned_to') else None,
            'done_ratio': issue_data.get('done_ratio', 0),
            'subject': issue_data.get('subject'),
            'description': issue_data.get('description', ''),
            'journals_count': len(journals),
            'last_journal_id': journals[-1].get('id') if journals else None,
            'attachments_count': len(attachments),
            'custom_fields': {
                cf.get('id'): cf.get('value')
                for cf in issue_data.get('custom_fields', [])
            },
        }

    def get_issue_snapshot(self, issue_id: int) -> Optional[Dict[str, Any]]:
        """Get issue snapshot"""
        return self._issue_snapshots.get(issue_id)

    def clear_issue_snapshot(self, issue_id: int):
        """Clear issue snapshot"""
        self._issue_snapshots.pop(issue_id, None)
    
    def list_issues(self, project_id: Optional[int] = None, status_id: Optional[int] = None, 
                   assigned_to_id: Optional[int] = None, tracker_id: Optional[int] = None,
                   priority_id: Optional[int] = None, author_id: Optional[int] = None,
                   created_on: Optional[str] = None, updated_on: Optional[str] = None,
                   limit: int = 100, offset: int = 0, sort: Optional[str] = None,
                   include: Optional[List[str]] = None) -> List[RedmineIssue]:
        """List issues"""
        # Validate query parameters
        query_params = {
            'project_id': project_id, 'status_id': status_id, 'assigned_to_id': assigned_to_id,
            'tracker_id': tracker_id, 'priority_id': priority_id, 'author_id': author_id,
            'created_on': created_on, 'updated_on': updated_on, 'limit': limit, 
            'offset': offset, 'sort': sort
        }
        
        try:
            validated_params = validate_and_clean_data(query_params, "query")
        except RedmineValidationError as e:
            raise RedmineAPIError(f"Query parameter validation failed: {e}")
        
        params = validated_params
        
        # Add additional parameters
        if include:
            params['include'] = ','.join(include)
        
        response = self._make_request('GET', '/issues.json', params=params)
        
        issues = []
        for issue_data in response.get('issues', []):
            issues.append(RedmineIssue(
                id=issue_data['id'],
                subject=issue_data['subject'],
                description=issue_data.get('description', ''),
                status=issue_data['status'],
                priority=issue_data['priority'],
                project=issue_data['project'],
                tracker=issue_data['tracker'],
                author=issue_data['author'],
                assigned_to=issue_data.get('assigned_to'),
                created_on=issue_data.get('created_on'),
                updated_on=issue_data.get('updated_on'),
                done_ratio=issue_data.get('done_ratio', 0)
            ))
        
        return issues
    
    def create_issue(self, project_id: int, subject: str, description: str = "",
                    tracker_id: Optional[int] = None, status_id: Optional[int] = None,
                    priority_id: Optional[int] = None, assigned_to_id: Optional[int] = None,
                    parent_issue_id: Optional[int] = None, custom_fields: Optional[List[Dict]] = None,
                    start_date: Optional[str] = None, due_date: Optional[str] = None,
                    estimated_hours: Optional[float] = None,
                    category_id: Optional[int] = None) -> int:
        """Create a new issue, return issue ID"""
        # Prepare validation data
        validation_data = {
            'project_id': project_id,
            'subject': subject,
            'description': description,
            'tracker_id': tracker_id,
            'status_id': status_id,
            'priority_id': priority_id,
            'assigned_to_id': assigned_to_id,
            'parent_issue_id': parent_issue_id,
            'custom_fields': custom_fields,
            'start_date': start_date,
            'due_date': due_date,
            'estimated_hours': estimated_hours,
            'category_id': category_id,
        }
        
        # Validate data
        try:
            validated_data = validate_and_clean_data(validation_data, "issue")
        except RedmineValidationError as e:
            raise RedmineAPIError(f"Issue data validation failed: {e}")
        
        issue_data = {'issue': validated_data}
        
        response = self._make_request('POST', '/issues.json', json=issue_data)
        
        if 'issue' not in response:
            raise RedmineAPIError("Failed to create issue: no issue data in response")
        
        return response['issue']['id']
    
    def update_issue(self, issue_id: int, **kwargs) -> bool:
        """Update issue"""
        update_data = {'issue': {}}
        
        # Supported update fields
        if 'subject' in kwargs:
            update_data['issue']['subject'] = kwargs['subject']
        if 'description' in kwargs:
            update_data['issue']['description'] = kwargs['description']
        if 'status_id' in kwargs:
            update_data['issue']['status_id'] = kwargs['status_id']
        if 'priority_id' in kwargs:
            update_data['issue']['priority_id'] = kwargs['priority_id']
        if 'assigned_to_id' in kwargs:
            update_data['issue']['assigned_to_id'] = kwargs['assigned_to_id']
        if 'done_ratio' in kwargs:
            update_data['issue']['done_ratio'] = kwargs['done_ratio']
        if 'tracker_id' in kwargs:
            update_data['issue']['tracker_id'] = kwargs['tracker_id']
        if 'parent_issue_id' in kwargs:
            # If parent_issue_id is None, remove the parent issue relationship
            if kwargs['parent_issue_id'] is None:
                update_data['issue']['parent_issue_id'] = ""
            else:
                update_data['issue']['parent_issue_id'] = kwargs['parent_issue_id']
        if 'start_date' in kwargs:
            update_data['issue']['start_date'] = kwargs['start_date']
        if 'due_date' in kwargs:
            update_data['issue']['due_date'] = kwargs['due_date']
        if 'estimated_hours' in kwargs:
            update_data['issue']['estimated_hours'] = kwargs['estimated_hours']
        if 'notes' in kwargs:
            update_data['issue']['notes'] = kwargs['notes']
        if 'category_id' in kwargs:
            update_data['issue']['category_id'] = kwargs['category_id']
        if 'custom_fields' in kwargs:
            update_data['issue']['custom_fields'] = kwargs['custom_fields']
        
        if not update_data['issue']:
            raise RedmineAPIError("No fields provided for update")
        
        self._make_request('PUT', f'/issues/{issue_id}.json', json=update_data)
        return True
    
    def delete_issue(self, issue_id: int) -> bool:
        """Delete issue"""
        self._make_request('DELETE', f'/issues/{issue_id}.json')
        return True
    
    def add_watcher(self, issue_id: int, user_id: int) -> bool:
        """Add issue watcher"""
        watcher_data = {'user_id': user_id}
        self._make_request('POST', f'/issues/{issue_id}/watchers.json', json=watcher_data)
        return True
    
    def remove_watcher(self, issue_id: int, user_id: int) -> bool:
        """Remove issue watcher"""
        self._make_request('DELETE', f'/issues/{issue_id}/watchers/{user_id}.json')
        return True
    
    def get_project(self, project_id: Union[int, str], include: Optional[List[str]] = None) -> RedmineProject:
        """Get project information"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        
        response = self._make_request('GET', f'/projects/{project_id}.json', params=params)
        
        if 'project' not in response:
            raise RedmineAPIError(f"Project {project_id} does not exist")
        
        project_data = response['project']
        return RedmineProject(
            id=project_data['id'],
            name=project_data['name'],
            identifier=project_data['identifier'],
            description=project_data.get('description', ''),
            status=project_data['status'],
            created_on=project_data.get('created_on'),
            updated_on=project_data.get('updated_on')
        )
    
    def list_projects(self, limit: int = 100, offset: int = 0) -> List[RedmineProject]:
        """List projects"""
        params = {
            'limit': limit,
            'offset': offset
        }
        
        response = self._make_request('GET', '/projects.json', params=params)
        
        projects = []
        for project_data in response.get('projects', []):
            projects.append(RedmineProject(
                id=project_data['id'],
                name=project_data['name'],
                identifier=project_data['identifier'],
                description=project_data.get('description', ''),
                status=project_data['status'],
                created_on=project_data.get('created_on'),
                updated_on=project_data.get('updated_on')
            ))
        
        return projects
    
    def create_project(self, name: str, identifier: str, description: str = "",
                      homepage: str = "", is_public: bool = True, parent_id: Optional[int] = None,
                      inherit_members: bool = False, tracker_ids: Optional[List[int]] = None,
                      enabled_module_names: Optional[List[str]] = None) -> int:
        """Create a new project, return project ID"""
        # Prepare validation data
        validation_data = {
            'name': name,
            'identifier': identifier,
            'description': description,
            'homepage': homepage,
            'is_public': is_public,
            'parent_id': parent_id,
            'inherit_members': inherit_members,
            'tracker_ids': tracker_ids,
            'enabled_module_names': enabled_module_names
        }
        
        # Validate data
        try:
            validated_data = validate_and_clean_data(validation_data, "project")
        except RedmineValidationError as e:
            raise RedmineAPIError(f"Project data validation failed: {e}")
        
        project_data = {'project': validated_data}
        
        response = self._make_request('POST', '/projects.json', json=project_data)
        
        if 'project' not in response:
            raise RedmineAPIError("Failed to create project: no project data in response")
        
        return response['project']['id']
    
    def update_project(self, project_id: Union[int, str], **kwargs) -> bool:
        """Update project"""
        update_data = {'project': {}}
        
        # Supported update fields
        for field in ['name', 'description', 'homepage', 'is_public', 'parent_id', 
                     'inherit_members', 'tracker_ids', 'enabled_module_names']:
            if field in kwargs:
                update_data['project'][field] = kwargs[field]
        
        if not update_data['project']:
            raise RedmineAPIError("No fields provided for update")
        
        self._make_request('PUT', f'/projects/{project_id}.json', json=update_data)
        return True
    
    def delete_project(self, project_id: Union[int, str]) -> bool:
        """Delete project"""
        self._make_request('DELETE', f'/projects/{project_id}.json')
        return True
    
    def archive_project(self, project_id: Union[int, str]) -> bool:
        """Archive project"""
        self._make_request('PUT', f'/projects/{project_id}/archive.json')
        return True
    
    def unarchive_project(self, project_id: Union[int, str]) -> bool:
        """Unarchive project"""
        self._make_request('PUT', f'/projects/{project_id}/unarchive.json')
        return True
    
    def get_issue_statuses(self) -> List[Dict[str, Any]]:
        """Get issue status list"""
        response = self._make_request('GET', '/issue_statuses.json')
        return response.get('issue_statuses', [])
    
    def get_priorities(self) -> List[Dict[str, Any]]:
        """Get priority list"""
        response = self._make_request('GET', '/enumerations/issue_priorities.json')
        return response.get('issue_priorities', [])
    
    def get_trackers(self) -> List[Dict[str, Any]]:
        """Get tracker list"""
        response = self._make_request('GET', '/trackers.json')
        return response.get('trackers', [])
    
    def get_time_entry_activities(self) -> List[Dict[str, Any]]:
        """Get time entry activity list"""
        response = self._make_request('GET', '/enumerations/time_entry_activities.json')
        return response.get('time_entry_activities', [])
    
    def get_document_categories(self) -> List[Dict[str, Any]]:
        """Get document category list"""
        response = self._make_request('GET', '/enumerations/document_categories.json')
        return response.get('document_categories', [])

    def get_issue_categories(self, project_id: int) -> List[Dict[str, Any]]:
        """Get project issue category list"""
        response = self._make_request('GET', f'/projects/{project_id}/issue_categories.json')
        return response.get('issue_categories', [])

    def _load_category_cache(self, project_id: int) -> Dict[str, int]:
        """Load issue category cache for the specified project (on-demand loading)"""
        if project_id in self._category_cache:
            return self._category_cache[project_id]

        try:
            categories = self.get_issue_categories(project_id)
            self._category_cache[project_id] = {
                item['name']: item['id'] for item in categories
            }
        except Exception:
            self._category_cache[project_id] = {}

        return self._category_cache[project_id]

    def find_category_id_by_name(self, project_id: int, name: str) -> Optional[int]:
        """Find the corresponding ID by issue category name (project level)"""
        cache = self._load_category_cache(project_id)
        return cache.get(name)

    def get_available_categories(self, project_id: int) -> Dict[str, int]:
        """Get all available issue category options for the specified project (name to ID mapping)"""
        return self._load_category_cache(project_id)

    def refresh_category_cache(self, project_id: int):
        """Refresh issue category cache for the specified project"""
        self._category_cache.pop(project_id, None)
        self._load_category_cache(project_id)

    def get_users(self, status: Optional[int] = None, name: Optional[str] = None,
                 group_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user list"""
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if status:
            params['status'] = status
        if name:
            params['name'] = name
        if group_id:
            params['group_id'] = group_id
        
        response = self._make_request('GET', '/users.json', params=params)
        return response.get('users', [])
    
    def get_user(self, user_id: Union[int, str], include: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get single user information"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        
        response = self._make_request('GET', f'/users/{user_id}.json', params=params)
        
        if 'user' not in response:
            raise RedmineAPIError(f"User {user_id} does not exist")
        
        return response['user']
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        response = self._make_request('GET', '/my/account.json')
        
        if 'user' not in response:
            raise RedmineAPIError("Unable to get current user information")
        
        return response['user']
    
    def list_users(self, limit: int = 20, offset: int = 0, status: int = None) -> List[RedmineUser]:
        """List users"""
        params = {
            'limit': min(max(limit, 1), 100),
            'offset': max(offset, 0)
        }
        
        if status is not None:
            params['status'] = status
        
        response = self._make_request('GET', '/users.json', params=params)
        
        users = []
        for user_data in response.get('users', []):
            users.append(RedmineUser(
                id=user_data['id'],
                login=user_data['login'],
                firstname=user_data.get('firstname', ''),
                lastname=user_data.get('lastname', ''),
                mail=user_data.get('mail', ''),
                status=user_data.get('status', 1),
                created_on=user_data.get('created_on'),
                last_login_on=user_data.get('last_login_on')
            ))
        
        return users
    
    def search_users(self, query: str, limit: int = 10) -> List[RedmineUser]:
        """Search users (by name or login)"""
        if not query.strip():
            return []
            
        params = {
            'name': query.strip(),
            'limit': min(max(limit, 1), 50)
        }
        
        response = self._make_request('GET', '/users.json', params=params)
        
        users = []
        for user_data in response.get('users', []):
            users.append(RedmineUser(
                id=user_data['id'],
                login=user_data['login'],
                firstname=user_data.get('firstname', ''),
                lastname=user_data.get('lastname', ''),
                mail=user_data.get('mail', ''),
                status=user_data.get('status', 1),
                created_on=user_data.get('created_on'),
                last_login_on=user_data.get('last_login_on')
            ))
        
        return users
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get specific user details"""
        response = self._make_request('GET', f'/users/{user_id}.json')
        
        if 'user' not in response:
            raise RedmineAPIError(f"User ID {user_id} not found")
        
        return response['user']
    
    def _load_enum_cache(self) -> Dict[str, Any]:
        """Load enumeration cache"""
        if self._enum_cache is not None:
            return self._enum_cache
            
        try:
            if self._cache_file.exists():
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    self._enum_cache = json.load(f)
                    
                # Check if domain matches
                cached_domain = self._enum_cache.get('domain')
                if cached_domain != self.config.redmine_domain:
                    # Domain mismatch, rebuild cache
                    self._refresh_enum_cache()
                    return self._enum_cache or {}
                    
                # Check if cache needs to be updated (older than 24 hours)
                cache_time = self._enum_cache.get('cache_time', 0)
                current_time = datetime.now().timestamp()
                if current_time - cache_time > 86400:  # 24 hours
                    self._refresh_enum_cache()
            else:
                self._refresh_enum_cache()
                
        except Exception:
            # Cache read failed, rebuild
            self._refresh_enum_cache()
            
        return self._enum_cache or {}
    
    def _refresh_enum_cache(self):
        """Refresh enumeration cache"""
        try:
            # Get all enumeration values
            priorities = self.get_priorities()
            statuses = self.get_issue_statuses()
            trackers = self.get_trackers()
            time_entry_activities = self.get_time_entry_activities()
            
            # Get user list (limit to 100 to avoid being too large)
            users = self.list_users(limit=100)
            
            # Build name-to-ID mapping
            user_by_name = {}
            user_by_login = {}
            for user in users:
                full_name = f"{user.firstname} {user.lastname}".strip()
                if full_name:
                    user_by_name[full_name] = user.id
                user_by_login[user.login] = user.id
            
            self._enum_cache = {
                'cache_time': datetime.now().timestamp(),
                'domain': self.config.redmine_domain,
                'priorities': {item['name']: item['id'] for item in priorities},
                'statuses': {item['name']: item['id'] for item in statuses},
                'trackers': {item['name']: item['id'] for item in trackers},
                'time_entry_activities': {item['name']: item['id'] for item in time_entry_activities},
                'users_by_name': user_by_name,
                'users_by_login': user_by_login
            }
            
            # Save to file
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._enum_cache, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            # Cache refresh failed, use empty cache
            self._enum_cache = {
                'cache_time': 0, 
                'domain': self.config.redmine_domain,
                'priorities': {}, 
                'statuses': {}, 
                'trackers': {},
                'time_entry_activities': {},
                'users_by_name': {},
                'users_by_login': {}
            }
    
    def find_priority_id_by_name(self, name: str) -> Optional[int]:
        """Find the corresponding ID by priority name"""
        cache = self._load_enum_cache()
        return cache.get('priorities', {}).get(name)
    
    def find_status_id_by_name(self, name: str) -> Optional[int]:
        """Find the corresponding ID by status name"""
        cache = self._load_enum_cache()
        return cache.get('statuses', {}).get(name)
    
    def find_tracker_id_by_name(self, name: str) -> Optional[int]:
        """Find the corresponding ID by tracker name"""
        cache = self._load_enum_cache()
        return cache.get('trackers', {}).get(name)
    
    def get_available_priorities(self) -> Dict[str, int]:
        """Get all available priority options (name to ID mapping)"""
        cache = self._load_enum_cache()
        return cache.get('priorities', {})
    
    def get_available_statuses(self) -> Dict[str, int]:
        """Get all available status options (name to ID mapping)"""
        cache = self._load_enum_cache()
        return cache.get('statuses', {})
    
    def get_available_trackers(self) -> Dict[str, int]:
        """Get all available tracker options (name to ID mapping)"""
        cache = self._load_enum_cache()
        return cache.get('trackers', {})
    
    def find_user_id_by_name(self, name: str) -> Optional[int]:
        """Find the corresponding ID by user name"""
        cache = self._load_enum_cache()
        return cache.get('users_by_name', {}).get(name)
    
    def find_user_id_by_login(self, login: str) -> Optional[int]:
        """Find the corresponding ID by user login"""
        cache = self._load_enum_cache()
        return cache.get('users_by_login', {}).get(login)
    
    def find_user_id(self, identifier: str) -> Optional[int]:
        """Find the corresponding ID by user name or login (smart query)"""
        cache = self._load_enum_cache()
        
        # Try name query first
        user_id = cache.get('users_by_name', {}).get(identifier)
        if user_id:
            return user_id
            
        # Then try login query
        return cache.get('users_by_login', {}).get(identifier)
    
    def get_available_users(self) -> Dict[str, Dict[str, int]]:
        """Get all available user options"""
        cache = self._load_enum_cache()
        return {
            'by_name': cache.get('users_by_name', {}),
            'by_login': cache.get('users_by_login', {})
        }
    
    def find_time_entry_activity_id_by_name(self, name: str) -> Optional[int]:
        """Find the corresponding ID by time entry activity name"""
        cache = self._load_enum_cache()
        return cache.get('time_entry_activities', {}).get(name)
    
    def get_available_time_entry_activities(self) -> Dict[str, int]:
        """Get all available time entry activity options (name to ID mapping)"""
        cache = self._load_enum_cache()
        return cache.get('time_entry_activities', {})
    
    def refresh_cache(self):
        """Manually refresh cache"""
        self._refresh_enum_cache()
    
    def create_time_entry(self, issue_id: int, hours: float, activity_id: int, 
                         comments: str = "", spent_on: Optional[str] = None,
                         user_id: Optional[int] = None) -> int:
        """Create time entry, return time entry ID
        
        Args:
            issue_id: Issue ID
            hours: Spent hours
            activity_id: Activity ID
            comments: Comments (optional)
            spent_on: Record date in YYYY-MM-DD format (optional, defaults to today)
            user_id: User ID (optional, defaults to current user)
            
        Returns:
            Time entry ID
        """
        from datetime import date
        
        # Prepare time entry data
        time_entry_data = {
            'issue_id': issue_id,
            'hours': hours,
            'activity_id': activity_id
        }
        
        if comments:
            time_entry_data['comments'] = comments
            
        if spent_on:
            time_entry_data['spent_on'] = spent_on
        else:
            time_entry_data['spent_on'] = date.today().strftime('%Y-%m-%d')
            
        if user_id:
            time_entry_data['user_id'] = user_id
        
        # Send request
        response = self._make_request('POST', '/time_entries.json', 
                                     json={'time_entry': time_entry_data})
        
        if 'time_entry' not in response:
            raise RedmineAPIError("Failed to create time entry: no time entry data in response")
            
        return response['time_entry']['id']
    

    def get_issue_journals(self, issue_id: int) -> List[Dict[str, Any]]:
        """Get all notes/journal records for an issue
        
        Args:
            issue_id: Issue ID
            
        Returns:
            List of notes, each note contains id, user, notes, created_on, details, and other fields
        """
        issue_data = self.get_issue_raw(issue_id, include=['journals'])
        return issue_data.get('journals', [])

    def test_connection(self) -> bool:
        """Test connection"""
        try:
            response = self._make_request('GET', '/my/account.json')
            return 'user' in response
        except RedmineAPIError:
            return False

    def get_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Get attachment details
        
        Args:
            attachment_id: Attachment ID
            
        Returns:
            Attachment information dictionary, containing id, filename, filesize, content_type, content_url, etc.
        """
        response = self._make_request('GET', f'/attachments/{attachment_id}.json')
        
        if 'attachment' not in response:
            raise RedmineAPIError(f"Attachment {attachment_id} does not exist")
        
        return response['attachment']
    
    def download_attachment(self, attachment_id: int) -> tuple[bytes, Dict[str, Any]]:
        """
        Download attachment content
        
        Args:
            attachment_id: Attachment ID
            
        Returns:
            (File binary content, attachment information dictionary)
        """
        # Get attachment information
        attachment = self.get_attachment(attachment_id)
        content_url = attachment.get('content_url')
        
        if not content_url:
            raise RedmineAPIError(f"Attachment {attachment_id} has no download link")
        
        # Download file (requires authentication)
        try:
            response = self.session.get(content_url, timeout=self.config.redmine_timeout)
            response.raise_for_status()
            return response.content, attachment
        except requests.exceptions.RequestException as e:
            raise RedmineAPIError(f"Failed to download attachment: {str(e)}")


# Global client instance
_client: Optional[RedmineClient] = None


def get_client() -> RedmineClient:
    """Get global client instance (singleton pattern)"""
    global _client
    if _client is None:
        _client = RedmineClient()
    return _client


def reload_client() -> RedmineClient:
    """Reload client (mainly used for testing)"""
    global _client
    _client = None
    return get_client()
