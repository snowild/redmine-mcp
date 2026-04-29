# Redmine Complete Setup Guide

This guide provides detailed Redmine initialization setup steps to ensure the redmine-mcp tools can be used properly.

## 🎯 Setup Overview

Redmine setup requires the following steps:
1. ✅ Enable REST API
2. ✅ Configure system basic data
3. ✅ Create projects
4. ✅ Get API key

## 📋 Detailed Setup Steps

### 1. Enable REST API
> **Must be performed as administrator**

1. Log in to the Redmine admin interface
2. Go to **Administration** → **Settings** → **API**
3. Check **"Enable REST web service (Web Service)"**
4. Click **Save**

### 2. Configure Roles and Permissions
> **Recommended minimum permission settings**

**Create Roles**
1. Go to **Administration** → **Roles and permissions**
2. Click **New role**
3. Create the following roles:

| Role Name | Recommended Permissions |
|---------|---------|
| Developer | View issues, Add issues, Edit issues, Add notes, Manage issue watchers |
| Tester | View issues, Add issues, Edit issues, Add notes |
| Project Manager | All issue-related permissions, View projects, Manage members |

**Key Permission Settings**
- ✅ **View issues** - Required for `get_issue`, `list_project_issues`, etc.
- ✅ **Add issues** - Required for `create_new_issue`
- ✅ **Edit issues** - Required for `update_issue_status`, `assign_issue`, etc.
- ✅ **Add notes** - Required for `add_issue_note`
- ✅ **Manage issue watchers** - Optional, for watcher features

### 3. Configure Trackers
> **Recommended basic tracker types**

1. Go to **Administration** → **Trackers**
2. Create the following trackers:

| Tracker Name | Purpose | Default Status |
|-----------|------|---------|
| Bug | Software bug tracking | New |
| Feature | New feature requests | New |
| Support | Technical support requests | New |

**Set Tracker Properties**
- Set the **default status** for each tracker
- Select applicable **custom fields** (if any)

### 4. Configure Issue Statuses
> **Recommended basic status settings**

1. Go to **Administration** → **Issue statuses**
2. Create the following statuses:

| Status Name | Is Closed | Purpose |
|---------|-----------|------|
| New | ❌ | Just created issue |
| In Progress | ❌ | Issue being processed |
| Waiting for Feedback | ❌ | Waiting for user response |
| Resolved | ❌ | Fixed but pending verification |
| Closed | ✅ | Completed issue |
| Rejected | ✅ | Issue that will not be handled |

**Important Settings**
- At least one "Closed" status is required (for the `close_issue` tool)
- Set appropriate **status colors** for visual distinction

### 6. Configure Issue Priorities
> **Define issue importance levels**

1. Go to **Administration** → **Enumerations** → **Issue priorities**
2. Create or edit priorities:

| Priority Name | Recommended Purpose | Set as Default |
|-----------|---------|---------|
| Low | Non-urgent improvements | ❌ |
| Normal | General issues | ✅ |
| High - Please handle this side | Important features or bugs, handle with priority | ❌ |
| Urgent - Handle within two days | Urgent issues, need to be handled within 2 days | ❌ |
| Critical - Handle immediately | Serious bugs, need immediate handling | ❌ |

### 7. Configure Time Tracking Activities
> **Define work types (if time tracking module is enabled)**

1. Go to **Administration** → **Enumerations** → **Activities (time tracking)**
2. Create activity types:

| Activity Name | Purpose | Set as Default |
|---------|------|---------|
| Design | System design and planning | ✅ |
| Development | Programming and coding | ❌ |
| Debug | Program bug fixes | ❌ |
| Investigation | Problem analysis and research | ❌ |
| Discussion | Meetings and technical discussions | ❌ |
| Testing | Testing and quality assurance | ❌ |
| Maintenance | System maintenance and support | ❌ |
| Documentation | Documentation writing and maintenance | ❌ |
| Teaching | Training and knowledge sharing | ❌ |
| Translation | Multilingual localization work | ❌ |
| Other | Other types of work | ❌ |

### 8. Configure Document Categories
> **Define document organization categories (if document module is enabled)**

1. Go to **Administration** → **Enumerations** → **Document categories**
2. Create document categories:

| Category Name | Purpose | Set as Default |
|---------|------|---------|
| User Manual | User operation manual and instructions | ✅ |
| Technical Documentation | Technical specifications and design documents | ❌ |
| Application Forms | Various applications and form documents | ❌ |
| Requirements Documents | System requirements and feature descriptions | ❌ |

### 9. Configure Workflow
> **Define status transition rules**

1. Go to **Administration** → **Workflow**
2. Select a **role** and **tracker** combination
3. Set allowed status transitions

**Recommended Basic Workflow**
```
New → In Progress → Resolved → Closed
  ↓      ↓        ↓
Waiting for Feedback ← ← ← ← ← ← ← ← ← (any status)
  ↓
Rejected
```

**Important Reminders**
- Ensure each role can perform basic status transitions
- Test critical path: New → In Progress → Closed
- Confirm the transition path required by the `close_issue` tool is available

### 10. Create Projects
> **Set up the first test project**

1. Go to **Projects** → **New project**
2. Fill in project information:
   - **Name**: Test Project
   - **Identifier**: test-project (used for API calls)
   - **Description**: Project for testing MCP tools
   - **Homepage**: (optional)

3. **Select Modules**:
   - ✅ Issue tracking
   - ✅ Time tracking (optional)
   - ✅ Documents (optional)
   - ✅ Files (optional)

4. **Set Trackers**:
   - Select tracker types to use in the project
   - Recommend at least selecting "Bug" and "Feature"

5. **Assign Members**:
   - Add users to the project
   - Assign appropriate roles

### 11. Verify Setup
> **Test whether basic functions are working properly**

**Test Using MCP Tools**
1. Get the API key and set environment variables
2. Run the following tests:

```bash
# Test connection
uv run python -c "
from redmine_mcp.server import health_check
print(health_check())
"

# Test project list
uv run python -c "
from redmine_mcp.server import get_projects
print(get_projects())
"

# Test status list
uv run python -c "
from redmine_mcp.server import get_issue_statuses
print(get_issue_statuses())
"

# Test tracker list
uv run python -c "
from redmine_mcp.server import get_trackers
print(get_trackers())
"

# Test priority list
uv run python -c "
from redmine_mcp.server import get_priorities
print(get_priorities())
"

# Test time tracking activity list
uv run python -c "
from redmine_mcp.server import get_time_entry_activities
print(get_time_entry_activities())
"

# Test document category list
uv run python -c "
from redmine_mcp.server import get_document_categories
print(get_document_categories())
"
```

**Manually Test Creating Issues**
1. Manually create a test issue in the project
2. Try changing the issue status
3. Test adding notes

## 🚨 Common Problems

### Problem: Cannot Create Issues
**Possible Causes**
- Workflow not properly configured
- Insufficient user permissions
- Tracker configuration issues

**Solutions**
1. Check if the workflow allows from "no status" to "New"
2. Confirm the user has "Add issues" permission in the project
3. Confirm the tracker is enabled and has a default status

### Problem: Cannot Update Issue Status
**Possible Causes**
- Workflow does not allow that status transition
- User role permissions are insufficient

**Solutions**
1. Check workflow settings
2. Confirm the user has "Edit issues" permission
3. Test manual status transition

### Problem: Cannot Find Projects or Issues
**Possible Causes**
- User does not have view permission
- Project status is archived

**Solutions**
1. Confirm the user is a project member
2. Check if the project status is "Active"
3. Confirm the user has "View issues" permission

## 📝 Setup Checklist

Before starting to use redmine-mcp, please confirm:

- [ ] ✅ REST API is enabled
- [ ] ✅ At least one role created (with basic issue permissions)
- [ ] ✅ At least one tracker created
- [ ] ✅ Basic issue statuses created (including at least one "Closed" status)
- [ ] ✅ Issue priorities configured (recommend at least: Low, Normal, High, Urgent)
- [ ] ✅ Time tracking activities configured (if using time tracking features)
- [ ] ✅ Document categories configured (if using document module)
- [ ] ✅ Basic workflow configured (allowing status transitions)
- [ ] ✅ At least one project created
- [ ] ✅ Users added to projects and assigned roles
- [ ] ✅ API key obtained
- [ ] ✅ Basic MCP functions tested

## 🔗 Related Resources

- [Redmine Administration Guide](https://www.redmine.org/projects/redmine/wiki/RedmineAdministration)
- [Redmine REST API Documentation](https://www.redmine.org/projects/redmine/wiki/Rest_api)
- [Workflow Setup](https://www.redmine.org/projects/redmine/wiki/RedmineWorkflow)
- [Roles and Permissions](https://www.redmine.org/projects/redmine/wiki/RedmineRoles)

---

After completing these settings, you can start using all features of redmine-mcp!
