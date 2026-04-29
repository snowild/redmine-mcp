# Redmine REST API User Guide

This document explains how to use the Redmine REST API for various operations, and integration with MCP tools.

## 🔑 API Authentication

### Get API Key

#### Automatic (Recommended)
```bash
cd redmine/scripts
python configure.py
```

#### Manual
1. Log in to Redmine: http://localhost:3000
2. Use `admin` / `admin` to log in
3. Go to **My Account** > **API Access Key**
4. Click the **Show** button
5. Copy the displayed key

#### Manual Test
```bash
cd redmine/scripts
python manual_api_setup.py
```

### API Key Format
```
Example: a1b2c3d4e5f6789012345678901234567890abcd
Length: 40-character hexadecimal string
```

## 📡 API Endpoints

### Basic Settings

#### HTTP Headers
```http
X-Redmine-API-Key: your_api_key_here
Content-Type: application/json
Accept: application/json
```

#### Base URL
```
http://localhost:3000
```

### Projects

#### Get All Projects
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/projects.json
```

#### Get Specific Project
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/projects/mcp-test.json
```

#### Create Project
```bash
curl -X POST \
     -H "X-Redmine-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "project": {
         "name": "Test Project",
         "identifier": "test-project",
         "description": "This is a test project"
       }
     }' \
     http://localhost:3000/projects.json
```

### Issues

#### Get All Issues
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/issues.json
```

#### Get Specific Issue
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/issues/1.json
```

#### Create Issue
```bash
curl -X POST \
     -H "X-Redmine-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "issue": {
         "project_id": 1,
         "subject": "Test Issue",
         "description": "This is a test issue description"
       }
     }' \
     http://localhost:3000/issues.json
```

#### Update Issue
```bash
curl -X PUT \
     -H "X-Redmine-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "issue": {
         "subject": "Updated issue title",
         "notes": "Add notes"
       }
     }' \
     http://localhost:3000/issues/1.json
```

#### Close Issue
```bash
curl -X PUT \
     -H "X-Redmine-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "issue": {
         "status_id": 5,
         "done_ratio": 100,
         "notes": "Issue completed"
       }
     }' \
     http://localhost:3000/issues/1.json
```

### Issue Statuses

#### Get All Statuses
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/issue_statuses.json
```

Expected response:
```json
{
  "issue_statuses": [
    {"id": 1, "name": "New"},
    {"id": 2, "name": "In Progress"},
    {"id": 3, "name": "Resolved"},
    {"id": 4, "name": "Feedback"},
    {"id": 5, "name": "Closed"},
    {"id": 6, "name": "Rejected"}
  ]
}
```

### Users

#### Get Current User
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/users/current.json
```

#### Get All Users
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/users.json
```

## 🔍 Advanced Queries

### Filtering and Sorting

#### Filter Issues by Project
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?project_id=1"
```

#### Filter by Status
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?status_id=open"
```

#### Pagination
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?limit=10&offset=0"
```

#### Sorting
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?sort=updated_on:desc"
```

#### Search
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?subject=~test"
```

### Include Related Data

#### Include Project Info
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues.json?include=project"
```

#### Include Multiple Info
```bash
curl -H "X-Redmine-API-Key: YOUR_KEY" \
     "http://localhost:3000/issues/1.json?include=journals,watchers,attachments"
```

## 🛠️ MCP Tool Integration

### Available MCP Tools

#### Basic Query Tools
- `server_info`: Server info
- `health_check`: Health check
- `get_projects`: Get project list
- `get_issue_statuses`: Get issue statuses

#### Issue Management Tools
- `get_issue`: Get issue details
- `list_project_issues`: List project issues
- `search_issues`: Search issues
- `get_my_issues`: Get my issues

#### Issue Operation Tools
- `create_new_issue`: Create new issue
- `update_issue_content`: Update issue content
- `update_issue_status`: Update issue status
- `add_issue_note`: Add issue note
- `assign_issue`: Assign issue
- `close_issue`: Close issue

### MCP Tool Examples

#### Direct Python Call
```python
from src.redmine_mcp.server import get_projects, create_new_issue

# Get project list
projects = get_projects()
print(projects)

# Create new issue
issue = create_new_issue(
    project_id=1,
    subject="Issue created via MCP",
    description="This is a test issue created using MCP tools"
)
print(issue)
```

#### Using in Claude Code
1. Configure MCP settings
2. Use natural language commands:
   - "Help me create a new issue"
   - "List all open issues"
   - "Update issue #5 status to completed"

## 📊 API Response Format

### Success Response
```json
{
  "issue": {
    "id": 1,
    "project": {
      "id": 1,
      "name": "MCP Test Project"
    },
    "subject": "Test Issue",
    "description": "Issue description",
    "status": {
      "id": 1,
      "name": "New"
    },
    "priority": {
      "id": 2,
      "name": "Normal"
    },
    "author": {
      "id": 1,
      "name": "admin"
    },
    "created_on": "2024-01-01T10:00:00Z",
    "updated_on": "2024-01-01T10:00:00Z"
  }
}
```

### Error Response
```json
{
  "errors": [
    "Subject cannot be blank"
  ]
}
```

## 🚨 Error Handling

### Common HTTP Status Codes

| Status Code | Description | Solution |
|-------------|-------------|----------|
| 200 | Success | - |
| 201 | Created | - |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Check resource ID |
| 422 | Validation Error | Check required fields |
| 500 | Server Error | Check Redmine logs |

### Debugging Tips

#### Enable Verbose Logging
```bash
export REDMINE_MCP_LOG_LEVEL=DEBUG
```

#### Check API Response
```bash
curl -v -H "X-Redmine-API-Key: YOUR_KEY" \
     http://localhost:3000/projects.json
```

#### Check Redmine Logs
```bash
cd redmine/docker
docker-compose logs redmine | grep -i error
```

## 🔒 Security Considerations

### API Key Protection
- Do not hardcode API keys in code
- Use environment variables to store sensitive information
- Rotate API keys regularly

### Access Control
- Create different users for different purposes
- Set appropriate project permissions
- Use the principle of least privilege

### Network Security
- Use HTTPS in production environments
- Configure firewall rules
- Monitor API usage

## 📈 Performance Optimization

### Batch Operations
```python
# Avoid: creating issues one by one
for i in range(100):
    create_issue(f"Issue {i}")

# Recommended: use batch API (if available)
batch_create_issues(issue_list)
```

### Cache Frequently Used Data
```python
# Cache project list
projects_cache = get_projects()

# Cache issue statuses
statuses_cache = get_issue_statuses()
```

### Pagination Handling
```python
def get_all_issues():
    issues = []
    offset = 0
    limit = 100
    
    while True:
        page = list_issues(limit=limit, offset=offset)
        if not page:
            break
        issues.extend(page)
        offset += limit
    
    return issues
```

## 📚 Reference Resources

### Official Documentation
- [Redmine REST API Documentation](https://www.redmine.org/projects/redmine/wiki/Rest_api)
- [Redmine User Guide](https://www.redmine.org/projects/redmine/wiki/User_Guide)

### Community Resources
- [Redmine Forum](https://www.redmine.org/boards)
- [Redmine GitHub](https://github.com/redmine/redmine)

### Related Tools
- [Postman Redmine Collection](https://www.postman.com/collections)
- [Redmine Python Client](https://pypi.org/project/python-redmine/)

## 🧪 Testing API

### Test Script
```python
#!/usr/bin/env python3
"""
API functionality test script
"""
import requests
import json

API_KEY = "your_api_key_here"
BASE_URL = "http://localhost:3000"
HEADERS = {
    "X-Redmine-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_api():
    # Test connection
    response = requests.get(f"{BASE_URL}/projects.json", headers=HEADERS)
    assert response.status_code == 200
    
    # Test creating project
    project_data = {
        "project": {
            "name": "API Test Project",
            "identifier": "api-test"
        }
    }
    response = requests.post(f"{BASE_URL}/projects.json", 
                           headers=HEADERS, 
                           json=project_data)
    assert response.status_code == 201
    
    print("✅ API test passed")

if __name__ == "__main__":
    test_api()
```

### Run Tests
```bash
cd redmine/scripts
python api_test.py
```
