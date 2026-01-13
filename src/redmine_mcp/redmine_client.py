"""
Redmine API 客戶端
負責與 Redmine 系統的 HTTP 通訊
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
    """Redmine 議題數據結構"""
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
    """Redmine 專案數據結構"""
    id: int
    name: str
    identifier: str
    description: str
    status: int
    created_on: Optional[str] = None
    updated_on: Optional[str] = None


@dataclass
class RedmineUser:
    """Redmine 用戶數據結構"""
    id: int
    login: str
    firstname: str
    lastname: str
    mail: str
    status: int
    created_on: Optional[str] = None
    last_login_on: Optional[str] = None


class RedmineAPIError(Exception):
    """Redmine API 錯誤"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RedmineClient:
    """Redmine API 客戶端"""
    
    def __init__(self):
        self.config = get_config()
        self.session = requests.Session()
        self.session.headers.update(self.config.api_headers)
        self.session.timeout = self.config.redmine_timeout
        
        # 快取相關設定
        self.cache_dir = Path.home() / ".redmine_mcp"
        self.cache_dir.mkdir(exist_ok=True)
        
        # 根據 domain 建立唯一的快取檔案名稱
        domain_hash = hash(self.config.redmine_domain)
        safe_domain = self.config.redmine_domain.replace('://', '_').replace('/', '_').replace(':', '_')
        self._cache_file = self.cache_dir / f"cache_{safe_domain}_{abs(domain_hash)}.json"
        self._enum_cache: Optional[Dict[str, Any]] = None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """執行 HTTP 請求"""
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
            
            # 使用友好的錯誤訊息
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
        """取得單一議題"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        
        response = self._make_request('GET', f'/issues/{issue_id}.json', params=params)
        
        if 'issue' not in response:
            raise RedmineAPIError(f"議題 {issue_id} 不存在")
        
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
        """取得單一議題的原始 API 資料（包含 journals 和 attachments）"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        
        response = self._make_request('GET', f'/issues/{issue_id}.json', params=params)
        
        if 'issue' not in response:
            raise RedmineAPIError(f"議題 {issue_id} 不存在")
        
        return response['issue']
    
    def list_issues(self, project_id: Optional[int] = None, status_id: Optional[int] = None, 
                   assigned_to_id: Optional[int] = None, tracker_id: Optional[int] = None,
                   priority_id: Optional[int] = None, author_id: Optional[int] = None,
                   created_on: Optional[str] = None, updated_on: Optional[str] = None,
                   limit: int = 100, offset: int = 0, sort: Optional[str] = None,
                   include: Optional[List[str]] = None) -> List[RedmineIssue]:
        """列出議題"""
        # 驗證查詢參數
        query_params = {
            'project_id': project_id, 'status_id': status_id, 'assigned_to_id': assigned_to_id,
            'tracker_id': tracker_id, 'priority_id': priority_id, 'author_id': author_id,
            'created_on': created_on, 'updated_on': updated_on, 'limit': limit, 
            'offset': offset, 'sort': sort
        }
        
        try:
            validated_params = validate_and_clean_data(query_params, "query")
        except RedmineValidationError as e:
            raise RedmineAPIError(f"查詢參數驗證失敗：{e}")
        
        params = validated_params
        
        # 加入額外參數
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
                    parent_issue_id: Optional[int] = None, custom_fields: Optional[List[Dict]] = None) -> int:
        """建立新議題，回傳議題 ID"""
        # 準備驗證資料
        validation_data = {
            'project_id': project_id,
            'subject': subject,
            'description': description,
            'tracker_id': tracker_id,
            'status_id': status_id,
            'priority_id': priority_id,
            'assigned_to_id': assigned_to_id,
            'parent_issue_id': parent_issue_id,
            'custom_fields': custom_fields
        }
        
        # 驗證資料
        try:
            validated_data = validate_and_clean_data(validation_data, "issue")
        except RedmineValidationError as e:
            raise RedmineAPIError(f"議題資料驗證失敗：{e}")
        
        issue_data = {'issue': validated_data}
        
        response = self._make_request('POST', '/issues.json', json=issue_data)
        
        if 'issue' not in response:
            raise RedmineAPIError("建立議題失敗：回應中沒有議題資料")
        
        return response['issue']['id']
    
    def update_issue(self, issue_id: int, **kwargs) -> bool:
        """更新議題"""
        update_data = {'issue': {}}
        
        # 支援的更新欄位
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
            # 如果 parent_issue_id 為 None，則移除父議題關係
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
        
        if not update_data['issue']:
            raise RedmineAPIError("沒有提供要更新的欄位")
        
        self._make_request('PUT', f'/issues/{issue_id}.json', json=update_data)
        return True
    
    def delete_issue(self, issue_id: int) -> bool:
        """刪除議題"""
        self._make_request('DELETE', f'/issues/{issue_id}.json')
        return True
    
    def add_watcher(self, issue_id: int, user_id: int) -> bool:
        """新增議題觀察者"""
        watcher_data = {'user_id': user_id}
        self._make_request('POST', f'/issues/{issue_id}/watchers.json', json=watcher_data)
        return True
    
    def remove_watcher(self, issue_id: int, user_id: int) -> bool:
        """移除議題觀察者"""
        self._make_request('DELETE', f'/issues/{issue_id}/watchers/{user_id}.json')
        return True
    
    def get_project(self, project_id: Union[int, str], include: Optional[List[str]] = None) -> RedmineProject:
        """取得專案資訊"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        
        response = self._make_request('GET', f'/projects/{project_id}.json', params=params)
        
        if 'project' not in response:
            raise RedmineAPIError(f"專案 {project_id} 不存在")
        
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
        """列出專案"""
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
        """建立新專案，回傳專案 ID"""
        # 準備驗證資料
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
        
        # 驗證資料
        try:
            validated_data = validate_and_clean_data(validation_data, "project")
        except RedmineValidationError as e:
            raise RedmineAPIError(f"專案資料驗證失敗：{e}")
        
        project_data = {'project': validated_data}
        
        response = self._make_request('POST', '/projects.json', json=project_data)
        
        if 'project' not in response:
            raise RedmineAPIError("建立專案失敗：回應中沒有專案資料")
        
        return response['project']['id']
    
    def update_project(self, project_id: Union[int, str], **kwargs) -> bool:
        """更新專案"""
        update_data = {'project': {}}
        
        # 支援的更新欄位
        for field in ['name', 'description', 'homepage', 'is_public', 'parent_id', 
                     'inherit_members', 'tracker_ids', 'enabled_module_names']:
            if field in kwargs:
                update_data['project'][field] = kwargs[field]
        
        if not update_data['project']:
            raise RedmineAPIError("沒有提供要更新的欄位")
        
        self._make_request('PUT', f'/projects/{project_id}.json', json=update_data)
        return True
    
    def delete_project(self, project_id: Union[int, str]) -> bool:
        """刪除專案"""
        self._make_request('DELETE', f'/projects/{project_id}.json')
        return True
    
    def archive_project(self, project_id: Union[int, str]) -> bool:
        """封存專案"""
        self._make_request('PUT', f'/projects/{project_id}/archive.json')
        return True
    
    def unarchive_project(self, project_id: Union[int, str]) -> bool:
        """解除封存專案"""
        self._make_request('PUT', f'/projects/{project_id}/unarchive.json')
        return True
    
    def get_issue_statuses(self) -> List[Dict[str, Any]]:
        """取得議題狀態列表"""
        response = self._make_request('GET', '/issue_statuses.json')
        return response.get('issue_statuses', [])
    
    def get_priorities(self) -> List[Dict[str, Any]]:
        """取得優先級列表"""
        response = self._make_request('GET', '/enumerations/issue_priorities.json')
        return response.get('issue_priorities', [])
    
    def get_trackers(self) -> List[Dict[str, Any]]:
        """取得追蹤器列表"""
        response = self._make_request('GET', '/trackers.json')
        return response.get('trackers', [])
    
    def get_time_entry_activities(self) -> List[Dict[str, Any]]:
        """取得時間追蹤活動列表"""
        response = self._make_request('GET', '/enumerations/time_entry_activities.json')
        return response.get('time_entry_activities', [])
    
    def get_document_categories(self) -> List[Dict[str, Any]]:
        """取得文件分類列表"""
        response = self._make_request('GET', '/enumerations/document_categories.json')
        return response.get('document_categories', [])
    
    def get_users(self, status: Optional[int] = None, name: Optional[str] = None,
                 group_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """取得用戶列表"""
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
        """取得單一用戶資訊"""
        params = {}
        if include:
            params['include'] = ','.join(include)
        
        response = self._make_request('GET', f'/users/{user_id}.json', params=params)
        
        if 'user' not in response:
            raise RedmineAPIError(f"用戶 {user_id} 不存在")
        
        return response['user']
    
    def get_current_user(self) -> Dict[str, Any]:
        """取得當前用戶資訊"""
        response = self._make_request('GET', '/my/account.json')
        
        if 'user' not in response:
            raise RedmineAPIError("無法取得當前用戶資訊")
        
        return response['user']
    
    def list_users(self, limit: int = 20, offset: int = 0, status: int = None) -> List[RedmineUser]:
        """列出用戶"""
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
        """搜尋用戶（依姓名或登入名）"""
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
        """取得特定用戶詳情"""
        response = self._make_request('GET', f'/users/{user_id}.json')
        
        if 'user' not in response:
            raise RedmineAPIError(f"找不到用戶 ID {user_id}")
        
        return response['user']
    
    def _load_enum_cache(self) -> Dict[str, Any]:
        """載入列舉值快取"""
        if self._enum_cache is not None:
            return self._enum_cache
            
        try:
            if self._cache_file.exists():
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    self._enum_cache = json.load(f)
                    
                # 檢查 domain 是否匹配
                cached_domain = self._enum_cache.get('domain')
                if cached_domain != self.config.redmine_domain:
                    # Domain 不匹配，重新建立快取
                    self._refresh_enum_cache()
                    return self._enum_cache or {}
                    
                # 檢查快取是否需要更新（超過24小時）
                cache_time = self._enum_cache.get('cache_time', 0)
                current_time = datetime.now().timestamp()
                if current_time - cache_time > 86400:  # 24小時
                    self._refresh_enum_cache()
            else:
                self._refresh_enum_cache()
                
        except Exception:
            # 快取讀取失敗，重新建立
            self._refresh_enum_cache()
            
        return self._enum_cache or {}
    
    def _refresh_enum_cache(self):
        """刷新列舉值快取"""
        try:
            # 取得所有列舉值
            priorities = self.get_priorities()
            statuses = self.get_issue_statuses()
            trackers = self.get_trackers()
            time_entry_activities = self.get_time_entry_activities()
            
            # 取得用戶列表（限制100個避免太大）
            users = self.list_users(limit=100)
            
            # 建立名稱到ID的對應
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
            
            # 儲存到檔案
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._enum_cache, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            # 快取刷新失敗，使用空快取
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
        """根據優先權名稱找到對應的 ID"""
        cache = self._load_enum_cache()
        return cache.get('priorities', {}).get(name)
    
    def find_status_id_by_name(self, name: str) -> Optional[int]:
        """根據狀態名稱找到對應的 ID"""
        cache = self._load_enum_cache()
        return cache.get('statuses', {}).get(name)
    
    def find_tracker_id_by_name(self, name: str) -> Optional[int]:
        """根據追蹤器名稱找到對應的 ID"""
        cache = self._load_enum_cache()
        return cache.get('trackers', {}).get(name)
    
    def get_available_priorities(self) -> Dict[str, int]:
        """取得所有可用的優先權選項（名稱到ID的對應）"""
        cache = self._load_enum_cache()
        return cache.get('priorities', {})
    
    def get_available_statuses(self) -> Dict[str, int]:
        """取得所有可用的狀態選項（名稱到ID的對應）"""
        cache = self._load_enum_cache()
        return cache.get('statuses', {})
    
    def get_available_trackers(self) -> Dict[str, int]:
        """取得所有可用的追蹤器選項（名稱到ID的對應）"""
        cache = self._load_enum_cache()
        return cache.get('trackers', {})
    
    def find_user_id_by_name(self, name: str) -> Optional[int]:
        """根據用戶姓名找到對應的 ID"""
        cache = self._load_enum_cache()
        return cache.get('users_by_name', {}).get(name)
    
    def find_user_id_by_login(self, login: str) -> Optional[int]:
        """根據用戶登入名找到對應的 ID"""
        cache = self._load_enum_cache()
        return cache.get('users_by_login', {}).get(login)
    
    def find_user_id(self, identifier: str) -> Optional[int]:
        """根據用戶姓名或登入名找到對應的 ID（智慧查詢）"""
        cache = self._load_enum_cache()
        
        # 先嘗試姓名查詢
        user_id = cache.get('users_by_name', {}).get(identifier)
        if user_id:
            return user_id
            
        # 再嘗試登入名查詢
        return cache.get('users_by_login', {}).get(identifier)
    
    def get_available_users(self) -> Dict[str, Dict[str, int]]:
        """取得所有可用的用戶選項"""
        cache = self._load_enum_cache()
        return {
            'by_name': cache.get('users_by_name', {}),
            'by_login': cache.get('users_by_login', {})
        }
    
    def find_time_entry_activity_id_by_name(self, name: str) -> Optional[int]:
        """根據時間追蹤活動名稱找到對應的 ID"""
        cache = self._load_enum_cache()
        return cache.get('time_entry_activities', {}).get(name)
    
    def get_available_time_entry_activities(self) -> Dict[str, int]:
        """取得所有可用的時間追蹤活動選項（名稱到ID的對應）"""
        cache = self._load_enum_cache()
        return cache.get('time_entry_activities', {})
    
    def refresh_cache(self):
        """手動刷新快取"""
        self._refresh_enum_cache()
    
    def create_time_entry(self, issue_id: int, hours: float, activity_id: int, 
                         comments: str = "", spent_on: Optional[str] = None,
                         user_id: Optional[int] = None) -> int:
        """建立時間記錄，回傳時間記錄 ID
        
        Args:
            issue_id: 議題 ID
            hours: 耗用工時
            activity_id: 活動 ID
            comments: 備註（可選）
            spent_on: 記錄日期 YYYY-MM-DD 格式（可選，預設今日）
            user_id: 用戶 ID（可選，預設當前用戶）
            
        Returns:
            時間記錄 ID
        """
        from datetime import date
        
        # 準備時間記錄資料
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
        
        # 發送請求
        response = self._make_request('POST', '/time_entries.json', 
                                     json={'time_entry': time_entry_data})
        
        if 'time_entry' not in response:
            raise RedmineAPIError("建立時間記錄失敗：回應中沒有時間記錄資料")
            
        return response['time_entry']['id']
    

    def get_issue_journals(self, issue_id: int) -> List[Dict[str, Any]]:
        """取得議題的所有備註/日誌記錄
        
        Args:
            issue_id: 議題 ID
            
        Returns:
            備註列表，每個備註包含 id, user, notes, created_on, details 等欄位
        """
        issue_data = self.get_issue_raw(issue_id, include=['journals'])
        return issue_data.get('journals', [])

    def test_connection(self) -> bool:
        """測試連線"""
        try:
            response = self._make_request('GET', '/my/account.json')
            return 'user' in response
        except RedmineAPIError:
            return False

    def get_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        取得附件的詳細資訊
        
        Args:
            attachment_id: 附件 ID
            
        Returns:
            附件資訊字典，包含 id, filename, filesize, content_type, content_url 等
        """
        response = self._make_request('GET', f'/attachments/{attachment_id}.json')
        
        if 'attachment' not in response:
            raise RedmineAPIError(f"附件 {attachment_id} 不存在")
        
        return response['attachment']
    
    def download_attachment(self, attachment_id: int) -> tuple[bytes, Dict[str, Any]]:
        """
        下載附件內容
        
        Args:
            attachment_id: 附件 ID
            
        Returns:
            (檔案二進位內容, 附件資訊字典)
        """
        # 取得附件資訊
        attachment = self.get_attachment(attachment_id)
        content_url = attachment.get('content_url')
        
        if not content_url:
            raise RedmineAPIError(f"附件 {attachment_id} 沒有下載連結")
        
        # 下載檔案（需帶認證）
        try:
            response = self.session.get(content_url, timeout=self.config.timeout)
            response.raise_for_status()
            return response.content, attachment
        except requests.exceptions.RequestException as e:
            raise RedmineAPIError(f"下載附件失敗: {str(e)}")


# 全域客戶端實例
_client: Optional[RedmineClient] = None


def get_client() -> RedmineClient:
    """取得全域客戶端實例（單例模式）"""
    global _client
    if _client is None:
        _client = RedmineClient()
    return _client


def reload_client() -> RedmineClient:
    """重新載入客戶端（主要用於測試）"""
    global _client
    _client = None
    return get_client()