# Usage Examples

This document provides detailed usage examples for the Redmine MCP Server, including actual conversation examples in Claude Code.

## 📋 Table of Contents

1. [Basic Operations](#basic-operations)
2. [Issue Management](#issue-management)
3. [Project Management](#project-management)
4. [Search Features](#search-features)
5. [Advanced Usage](#advanced-usage)

## 🔧 Basic Operations

### Check Service Status

**User Input:**
```
Please check Redmine MCP server status
```

**Claude Response:**
```
✓ Server is running normally, connected to https://your-redmine.com
```

### Get Server Information

**User Input:**
```
Show server information
```

**Claude Response:**
```
Redmine MCP Server is running
- Redmine Domain: https://your-redmine.com
- Debug Mode: false
- API Timeout: 30 seconds
```

## 📝 Issue Management

### View Issue Details

**User Input:**
```
Get detailed information for issue #123
```

**Claude Response:**
```
Issue #123: Fix User Login Issue

Basic Information:
- Project: E-commerce Website (ID: 1)
- Tracker: Bug
- Status: In Progress
- Priority: High
- Created by: Zhang San
- Assigned to: Li Si
- Completion: 30%
- Created: 2024-01-15
- Updated: 2024-01-20

Description:
Users report inability to log in to the system normally, error message shows "Invalid credentials"
```

### Create New Issue

**User Input:**
```
Create a new issue in project ID 1:
- Title: Optimize search performance
- Description: Current search response time is too long, performance optimization needed
- Tracker ID: 2 (Feature)
- Priority ID: 3 (Medium)
```

**Claude Response:**
```
New issue created successfully!

Issue ID: #156
Title: Optimize search performance
Project: E-commerce Website
Tracker: Feature
Status: New
Priority: Medium
Assigned to: Unassigned

Description:
Current search response time is too long, performance optimization needed
```

### Update Issue Status

**User Input:**
```
Update issue #123 status to "Resolved", and add note "Login verification logic has been fixed"
```

**Claude Response:**
```
Issue status updated successfully!

Issue: #123 - Fix User Login Issue
New Status: Resolved
Note: Login verification logic has been fixed
```

### Update Issue Content

**User Input:**
```
Update issue #156 completion percentage to 60%, and change description to "Preliminary performance analysis completed"
```

**Claude Response:**
```
Issue content updated successfully!

Issue: #156 - Optimize search performance
Updated Fields:
- Description updated
- Completion: 60%

Current Status:
- Status: In Progress
- Priority: Medium
- Completion: 60%
```

### Assign Issue

**User Input:**
```
Assign issue #156 to user ID 5, note "Please assist with performance testing"
```

**Claude Response:**
```
Issue assignment updated successfully!

Issue: #156 - Optimize search performance
Action: Assigned to user ID 5
Currently assigned to: Wang Wu
Note: Please assist with performance testing
```

### Add Issue Note

**User Input:**
```
Add note "Test results: login function working normally" to issue #123
```

**Claude Response:**
```
Note added successfully!

Issue: #123 - Fix User Login Issue
Note Type: Public
Note Content:
Test results: login function working normally
```

### Close Issue

**User Input:**
```
Close issue #123, set completion to 100%, note "Issue resolved and tested"
```

**Claude Response:**
```
Issue closed successfully!

Issue: #123 - Fix User Login Issue
Status: Closed
Completion: 100%
Close Note: Issue resolved and tested
```

## 🗂️ Project Management

### Get Project List

**User Input:**
```
Show all accessible projects
```

**Claude Response:**
```
Found 3 projects:

ID    Identifier           Name                           Status
----- -------------------- ------------------------------ ----
1     ecommerce-website    E-commerce Website             Active
2     mobile-app           Mobile Application             Active
3     internal-tools       Internal Tools                 Archived
```

### List Project Issues

**User Input:**
```
Show all open issues in project 1, limit 10
```

**Claude Response:**
```
Project: E-commerce Website
Status Filter: open
Found 8 issues:

ID       Title                                     Status       Assigned to     Updated
-------- ---------------------------------------- ------------ --------------- ----------
156      Optimize search performance               In Progress  Wang Wu         2024-01-20
154      Add shopping cart reminder feature        New          Unassigned      2024-01-19
152      Fix product image loading issue           In Progress  Li Si           2024-01-18
```

## 🔍 Search Features

### Keyword Search

**User Input:**
```
Search for issues containing the keyword "performance"
```

**Claude Response:**
```
Search keyword: 'performance'
Found 3 related issues:

ID       Title                                 Status       Project
-------- ------------------------------------ ------------ ---------------
156      Optimize search performance           In Progress  E-commerce Website
143      Website loading speed optimization    Resolved     E-commerce Website
128      Database query performance tuning     In Progress  Internal Tools
```

### Project-specific Search

**User Input:**
```
Search for issues containing "login" in project 1
```

**Claude Response:**
```
Search keyword: 'login'
Search scope: Project 1
Found 2 related issues:

ID       Title                                 Status       Project
-------- ------------------------------------ ------------ ---------------
123      Fix user login issue                  Closed       E-commerce Website
145      Third-party login integration         New          E-commerce Website
```

### My Issues

**User Input:**
```
Show all open issues assigned to me
```

**Claude Response:**
```
Issues assigned to Zhang San:
Status Filter: open
Found 4 issues:

ID       Title                                 Project            Status       Updated
-------- ------------------------------------ --------------- ------------ ----------
161      Implement user permission management  E-commerce Website New          2024-01-21
159      Optimize database indexes             Internal Tools     In Progress  2024-01-20
157      Update API documentation              E-commerce Website In Progress  2024-01-19
155      Fix mobile UI issue                 Mobile Application New          2024-01-18
```

## 🚀 Advanced Usage

### Batch Operation Example

**User Input:**
```
Please help me complete the following operations:
1. Get all new status issues in project 1
2. Assign issues with priority "High" to user ID 3
3. Add note "Assigned for handling" to each assigned issue
```

**Claude will automatically execute these steps:**

```
1. Getting new issues in project 1...

Project: E-commerce Website
Status Filter: open
Found 3 new issues:
- #154: Add shopping cart reminder feature (Priority: High)
- #158: Update product category page (Priority: Medium)
- #160: Add customer review feature (Priority: High)

2. Assigning issues with priority "High"...

Issue #154 assigned to user ID 3 successfully
Issue #160 assigned to user ID 3 successfully

3. Adding notes...

Note added to issue #154 successfully
Note added to issue #160 successfully

✅ Batch operation complete! 2 high priority issues assigned to user ID 3.
```

### Workflow Automation

**User Input:**
```
Help me create a new Bug report workflow:
1. Create issue "Fix product page loading error"
2. Set to high priority
3. Assign to QA team lead (user ID 7)
4. Add preliminary analysis note
```

**Claude Execution Flow:**

```
🔄 Executing Bug report workflow...

Step 1: Create new issue
New issue created successfully!
Issue ID: #162
Title: Fix product page loading error

Step 2: Set high priority
Issue content updated successfully!
Updated Fields:
- Priority ID: 4

Step 3: Assign to QA lead
Issue assignment updated successfully!
Currently assigned to: QA-Leader

Step 4: Add analysis note
Note added successfully!
Note content: Preliminary error reproduction and environment analysis needed

✅ Bug report workflow complete! Issue #162 has been created and is ready to start processing.
```

## 📊 System Status Queries

### Get Issue Status List

**User Input:**
```
Show all available issue statuses
```

**Claude Response:**
```
Available issue statuses:

ID    Name              Closed
----- --------------- --------
1     New             No
2     In Progress     No
3     Resolved        No
4     Feedback        No
5     Closed          Yes
6     Rejected        Yes
```

## 💡 Best Practices

### 1. Issue Description Writing
```
When creating an issue, include:
- Problem description
- Reproduction steps
- Expected results
- Actual results
- Environment information
```

### 2. Status Update Habits
```
Regularly update issue status and add meaningful notes:
- Explain current progress
- Issues encountered
- Next steps
```

### 3. Search Tips
```
Use specific keywords to search:
- Feature names (e.g., "login", "search")
- Error types (e.g., "500 error", "loading failed")
- Component names (e.g., "shopping cart", "user interface")
```

## 🔧 Troubleshooting Examples

### Permission Issues
**Error Message:**
```
Insufficient permissions: You do not have permission to perform this operation
```

**Solution:**
1. Confirm the user corresponding to the API key has sufficient permissions
2. Check if the project is public or if the user is a project member
3. Confirm user role settings

### Connection Issues
**Error Message:**
```
Connection failed: Please check network connection and Redmine server status
```

**Solution:**
1. Check network connection
2. Confirm Redmine server is operating normally
3. Check firewall settings
4. Adjust timeout settings

---

For more usage tips and examples, please refer to [README.md](../README.md) or open an Issue to ask.
