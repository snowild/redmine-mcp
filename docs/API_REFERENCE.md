# API Reference

This document provides a detailed description of all MCP tools provided by the Redmine MCP Server and their parameters.

## 📋 Table of Contents

1. [Basic Tools](#basic-tools)
2. [Issue Query Tools](#issue-query-tools)
3. [Issue Operation Tools](#issue-operation-tools)
4. [Project Management Tools](#project-management-tools)
5. [Search Tools](#search-tools)
6. [Parameter Type Reference](#parameter-type-reference)
7. [Error Handling](#error-handling)

## 🔧 Basic Tools

### server_info

Get server information and status.

**Parameters:** None

**Returns:**
```
Redmine MCP Server is running
- Redmine Domain: https://your-redmine.com
- Debug Mode: false
- API Timeout: 30 seconds
```

**Usage Example:**
```python
# In Claude Code
Show server information
```

---

### health_check

Health check tool to confirm the server is operating normally.

**Parameters:** None

**Returns:**
- Success: `✓ Server is running normally, connected to {domain}`
- Failure: `✗ Unable to connect to Redmine server: {domain}` or `✗ Server error: {error}`

**Usage Example:**
```python
# In Claude Code
Run health check
```

## 📄 Issue Query Tools

### get_issue

Get detailed information for a specified Redmine issue.

**Parameters:**
- `issue_id` (int, required): Issue ID
- `include_details` (bool, optional): Whether to include detailed information (default true)

**Returns:** Detailed issue information, including basic information and description

**Usage Example:**
```python
# In Claude Code
Get detailed information for issue #123
Get basic information for issue #456 (without detailed data)
```

---

### list_project_issues

List issues in a project.

**Parameters:**
- `project_id` (int, required): Project ID
- `status_filter` (str, optional): Status filter, options "open", "closed", "all" (default "open")
- `limit` (int, optional): Maximum number of results, range 1-100 (default 20)

**Returns:** Project issue list, displayed in table format

**Usage Example:**
```python
# In Claude Code
List all open issues in project 1
Show closed issues in project 2, limit 10
List all issues in project 3
```

---

### get_my_issues

Get a list of issues assigned to the current user.

**Parameters:**
- `status_filter` (str, optional): Status filter, options "open", "closed", "all" (default "open")
- `limit` (int, optional): Maximum number of results, range 1-100 (default 20)

**Returns:** Current user's issue list

**Usage Example:**
```python
# In Claude Code
Show all my open issues
Get my completed issues, limit 15
```

## ✏️ Issue Operation Tools

### create_new_issue

Create a new Redmine issue.

**Parameters:**
- `project_id` (int, required): Project ID
- `subject` (str, required): Issue title
- `description` (str, optional): Issue description
- `tracker_id` (int, optional): Tracker ID
- `priority_id` (int, optional): Priority ID
- `assigned_to_id` (int, optional): User ID to assign to

**Returns:** Creation result message, including new issue basic information

**Usage Example:**
```python
# In Claude Code
Create issue "Fix login error" in project 1, description "Users cannot log in normally"
Create issue: title "New feature development", project ID 2, tracker ID 2, priority ID 3
```

---

### update_issue_status

Update issue status.

**Parameters:**
- `issue_id` (int, required): Issue ID
- `status_id` (int, required): New status ID
- `notes` (str, optional): Update note

**Returns:** Update result message

**Usage Example:**
```python
# In Claude Code
Update issue #123 status to 3 (Resolved)
Update issue #456 status to 2, note "Starting to handle this issue"
```

---

### update_issue_content

Update issue content (title, description, priority, completion percentage, etc.).

**Parameters:**
- `issue_id` (int, required): Issue ID
- `subject` (str, optional): New issue title
- `description` (str, optional): New issue description
- `priority_id` (int, optional): New priority ID
- `done_ratio` (int, optional): New completion percentage 0-100

**Returns:** Update result message

**Usage Example:**
```python
# In Claude Code
Update issue #123 title to "Fix user login issue"
Set issue #456 completion percentage to 80%
Update issue #789 description and priority
```

---

### add_issue_note

Add a note to an issue.

**Parameters:**
- `issue_id` (int, required): Issue ID
- `notes` (str, required): Note content
- `private` (bool, optional): Whether it is a private note (default false)

**Returns:** Add result message

**Usage Example:**
```python
# In Claude Code
Add note "Preliminary analysis completed" to issue #123
Add private note "Internal discussion results" to issue #456
```

---

### assign_issue

Assign an issue to a user.

**Parameters:**
- `issue_id` (int, required): Issue ID
- `user_id` (int, optional): User ID to assign to (if None, unassign)
- `notes` (str, optional): Assignment note

**Returns:** Assignment result message

**Usage Example:**
```python
# In Claude Code
Assign issue #123 to user ID 5
Unassign issue #456
Assign issue #789 to user 3, note "Please assist with handling"
```

---

### close_issue

Close an issue (set to completed status).

**Parameters:**
- `issue_id` (int, required): Issue ID
- `notes` (str, optional): Close note
- `done_ratio` (int, optional): Completion percentage (default 100)

**Returns:** Close result message

**Usage Example:**
```python
# In Claude Code
Close issue #123
Close issue #456, note "Issue resolved"
Close issue #789, completion percentage 100%, note "Test passed"
```

## 🗂️ Project Management Tools

### get_projects

Get a list of accessible projects.

**Parameters:** None

**Returns:** Formatted project list, including ID, identifier, name, status

**Usage Example:**
```python
# In Claude Code
Show all accessible projects
Get project list
```

---

### get_issue_statuses

Get a list of all available issue statuses.

**Parameters:** None

**Returns:** Formatted status list, including ID, name, whether closed

**Usage Example:**
```python
# In Claude Code
Show all available issue statuses
Get status list
```

## 🔍 Search Tools

### search_issues

Search for issues (search for keywords in title or description).

**Parameters:**
- `query` (str, required): Search keyword
- `project_id` (int, optional): Limit search to a specific project
- `limit` (int, optional): Maximum number of results, range 1-50 (default 10)

**Returns:** List of issues matching the search criteria

**Usage Example:**
```python
# In Claude Code
Search for issues containing "login"
Search for "performance" related issues in project 1
Search for "error" keyword, limit 20 results
```

## 📝 Parameter Type Reference

### Data Types

| Type | Description | Example |
|------|-------------|---------|
| `int` | Integer | `123`, `0`, `-5` |
| `str` | String | `"Issue Title"`, `"Note content"` |
| `bool` | Boolean | `true`, `false` |

### Common ID Mappings

#### Status ID (status_id)
Typical mappings (may vary depending on Redmine configuration):
- `1`: New
- `2`: In Progress
- `3`: Resolved
- `4`: Feedback
- `5`: Closed
- `6`: Rejected

#### Priority ID (priority_id)
Typical mappings:
- `1`: Low
- `2`: Normal
- `3`: High
- `4`: Urgent
- `5`: Immediate

#### Tracker ID (tracker_id)
Typical mappings:
- `1`: Bug
- `2`: Feature
- `3`: Support

### Special Values

#### status_filter Parameter
- `"open"`: All issues with open status
- `"closed"`: All issues with closed status
- `"all"`: All status issues

## ⚠️ Error Handling

### Common Error Types

#### Authentication Error
```
Authentication failed: Please check if the API key is correct
```
**Solution:** Check the `REDMINE_API_KEY` setting in the `.env` file

#### Permission Error
```
Insufficient permissions: You do not have permission to perform this operation
```
**Solution:** Confirm the user has sufficient permissions to perform the operation

#### Resource Not Found
```
Specified issue not found, please confirm the issue ID is correct
```
**Solution:** Check if the provided ID is correct

#### Data Validation Error
```
Data format error: Please check if the input data meets the requirements
```
**Solution:** Check parameter format and required fields

#### Connection Error
```
Connection failed: Please check network connection and Redmine server status
```
**Solution:** Check network connection and server status

### Debug Mode

Enable debug mode to get more detailed error information:

```env
DEBUG_MODE=true
```

### Parameter Validation

All tools include parameter validation:

#### Required Parameter Check
- Ensure all required parameters are provided
- Check if parameter types are correct

#### Value Range Check
- `limit` parameter is restricted to reasonable ranges
- `done_ratio` must be between 0-100
- ID parameters must be positive integers

#### String Length Check
- Issue title must not exceed 255 characters
- Description must not exceed 65535 characters

## 🔄 Tool Execution Flow

### 1. Parameter Validation
All input parameters are validated to ensure correct format

### 2. API Call
Use Redmine REST API to perform actual operations

### 3. Result Processing
Convert API responses to user-friendly interface format

### 4. Error Handling
Catch and convert error messages into easy-to-understand explanations

## 💡 Best Practices

### Parameter Usage Recommendations

1. **Use meaningful IDs**
   ```python
   # Good practice
   Get detailed information for issue #123
   
   # Avoid
   Get detailed information for issue #999999 (non-existent ID)
   ```

2. **Provide complete descriptions**
   ```python
   # Good practice
   Create issue "Fix user login issue", description "Users report inability to log in normally, error message is 500 error"
   
   # Avoid
   Create issue "Fix" (description too brief)
   ```

3. **Appropriate pagination limits**
   ```python
   # Good practice
   List issues in project 1, limit 20
   
   # Avoid
   List issues in project 1, limit 1000 (may affect performance)
   ```

### Workflow Recommendations

1. **Query before operating**
   ```python
   # Recommended workflow
   1. Get project list
   2. Select target project
   3. Create or update issue
   ```

2. **Provide appropriate notes**
   ```python
   # Good practice
   Add meaningful notes explaining progress or change reasons when updating issue status
   ```

---

For more details, please refer to [Usage Examples](USAGE_EXAMPLES.md) or [README.md](../README.md).
