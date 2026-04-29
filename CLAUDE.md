# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server project for integrating with Redmine systems. Uses Python 3.12+ and the uv package manager.

## Development Environment Setup

### Dependency Management
- Use `uv` as the package manager
- Install dependencies: `uv sync`
- Run tests: `uv run python -m pytest`

### Project Structure
```
redmine-mcp/
├── src/redmine_mcp/          # Main source code
│   ├── __init__.py           # Package initialization
│   ├── server.py             # MCP server main program ✓ Completed
│   ├── redmine_client.py     # Redmine API client ✓ Completed
│   ├── config.py             # Configuration management ✓ Completed
├── tests/                    # Test files
├── docs/                     # Documentation directory
│   ├── issues/               # Development issue records
│   └── manuals/              # Technical manuals
├── pyproject.toml            # Project configuration and dependencies
├── uv.lock                   # Locked dependency versions
└── .env                      # Environment variables (to be created)
```

## MCP Development Notes

### Technology Stack
- **MCP SDK**: mcp[cli] >= 1.9.4 (uses FastMCP)
- **HTTP Client**: requests >= 2.31.0
- **Configuration Management**: python-dotenv >= 1.0.0
- **Image Processing**: Pillow >= 10.0.0
- **Python Version**: >= 3.12

### MCP Server Architecture
- Uses FastMCP to build the server
- Tool registration uses the `@mcp.tool()` decorator
- Supports asynchronous operations and type safety

### Redmine API Integration
- **Issue Management**: Query, create, update, delete issues
- **Project Management**: Query, create, update, delete, archive projects
- **User Management**: Query users, get current user information
- **Metadata Queries**: Status, priority, tracker lists
- **Watcher Management**: Add/remove issue watchers
- **Full Filter Support**: Multi-condition filtering and sorting

## Claude Code Integration

### Install to Claude Code
```bash
# Install MCP server
uv tool install .

# Or using pip
pip install .

# Add to Claude Code
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here" \
  -e REDMINE_MCP_LOG_LEVEL="INFO" \
  -e REDMINE_MCP_TIMEOUT="30"
```

### Environment Variable Reference

To avoid conflicts with other projects' environment variables, redmine-mcp uses a dedicated prefix:

- **Required Variables**:
  - `REDMINE_DOMAIN`: Redmine server URL
  - `REDMINE_API_KEY`: Redmine API key

- **Log Level Control**:
  - `REDMINE_MCP_LOG_LEVEL`: Project-specific log level (default: INFO)
  - `FASTMCP_LOG_LEVEL`: Built-in FastMCP variable (optional)
    - If not set, the system will automatically use the value of `REDMINE_MCP_LOG_LEVEL`
    - Setting this variable allows separate control of FastMCP log output

- **Other Configuration**:
  - `REDMINE_MCP_TIMEOUT`: Request timeout (seconds)
  - `REDMINE_TIMEOUT`: Backward-compatible timeout setting

### Available MCP Tools (26)
- **Management Tools**: server_info, health_check, refresh_cache
- **Query Tools**: get_issue, list_project_issues, get_projects, get_issue_statuses, get_trackers, get_priorities, get_time_entry_activities, get_document_categories, search_issues, get_my_issues
- **Journal Tools**: list_issue_journals, get_journal
- **Attachment Tools**: get_attachment_info, get_attachment_image ✨ New (supports thumbnail and visual analysis)
- **User Tools**: search_users, list_users, get_user
- **Editing Tools**: update_issue_status, update_issue_content, add_issue_note (supports time entry recording), assign_issue, close_issue
- **Creation Tools**: create_new_issue (supports name parameters)

## Common Commands

```bash
# Install dependencies
uv sync

# Run MCP server
uv run python -m redmine_mcp.server

# Test Claude Code integration
uv run python tests/scripts/claude_integration.py

# Run unit tests
uv run python -m pytest tests/unit/

# Run all tests
uv run python -m pytest tests/

# Add new dependencies
uv add <package-name>
```

## Smart Cache System ✨

### Cache Mechanism Features
- **Multi-Domain Support**: Automatically creates independent cache files based on Redmine domain
- **Auto-Update**: Cache data automatically refreshes every 24 hours
- **Full Coverage**: Caches enum values (priority, status, tracker) and user data
- **File Location**: `~/.redmine_mcp/cache_{domain}_{hash}.json`

### Available Helper Functions
```python
client = get_client()

# Enum value queries
priority_id = client.find_priority_id_by_name("Low")           # → 5
status_id = client.find_status_id_by_name("In Progress")       # → 2
tracker_id = client.find_tracker_id_by_name("Bug")            # → 1

# User queries
user_id = client.find_user_id("Redmine Admin")              # Smart query (name or login)
user_id = client.find_user_id_by_name("Redmine Admin")      # Name-only query
user_id = client.find_user_id_by_login("admin")             # Login-only query

# Time entry activity queries
activity_id = client.find_time_entry_activity_id_by_name("Development")  # → 11

# Get all options
priorities = client.get_available_priorities()              # {"Low": 5, "Normal": 6, ...}
users = client.get_available_users()                        # {"by_name": {...}, "by_login": {...}}
activities = client.get_available_time_entry_activities()   # {"Design": 10, "Development": 11, ...}

# Manual refresh
client.refresh_cache()
```

### MCP Tools
- `refresh_cache()`: Manually refresh cache and display statistics

## Name Parameter Support ✨

### MCP Tools Supporting Name Parameters
The following tools now support using names instead of just IDs:

```python
# Update issue status (using name)
update_issue_status(issue_id=1, status_name="In Progress")

# Update issue content (using name)
update_issue_content(
    issue_id=1,
    priority_name="High",
    tracker_name="Bug"
)

# Assign issue (using name)
assign_issue(issue_id=1, user_name="Redmine Admin")
assign_issue(issue_id=1, user_login="admin")

# Create new issue (using name)
create_new_issue(
    project_id=1,
    subject="New Feature Development",
    priority_name="Normal",
    tracker_name="Feature",
    assigned_to_name="Redmine Admin"
)
```

### Error Handling
If the provided name does not exist, the tool will automatically display available options:
```
Priority name not found: "Ultra High"

Available priorities:
- Low
- Normal
- High
- Urgent
```

## Journal Query Feature ✨

### List Issue Journals
Use `list_issue_journals` to list all journal/note records for an issue:

```python
# List records with journal content
list_issue_journals(issue_id=123)

# Include property change records (status, priority, etc. changes)
list_issue_journals(issue_id=123, include_property_changes=True)
```

Output example:
```
Journal records for issue #123 (3 total):
==================================================

📝 Journal #456
   Author: Zhang San
   Time: 2025-01-15T10:30:00Z
   Note content:
      Preliminary testing completed

📝 Journal #457
   Author: Li Si
   Time: 2025-01-16T14:20:00Z
   🔒 Private note
   Note content:
      Internal discussion record
```

### Get Single Journal Details
Use `get_journal` to get complete information for a specific journal:

```python
# Get Journal #456 from issue #123
get_journal(issue_id=123, journal_id=456)
```

Output includes:
- Journal ID and associated issue
- Author information (name and ID)
- Creation time
- Note content
- Property change details (old value → new value)

## Attachment Image Visual Analysis Feature ✨

### Get Attachment Information
Use `get_attachment_info` to get detailed attachment information (without downloading the file):

```python
# Get attachment information
get_attachment_info(attachment_id=123)
```

Output includes: file name, size, type, uploader, upload time, download link

### Visual Analysis of Image Attachments
Use `get_attachment_image` to download images for AI visual analysis:

```python
# Use thumbnail mode (default, reduces token consumption)
get_attachment_image(attachment_id=123)

# Specify thumbnail maximum size
get_attachment_image(attachment_id=123, max_size=600)

# Get original size image (no thumbnail)
get_attachment_image(attachment_id=123, thumbnail=False)
```

### Usage Flow Example
```
1. get_issue(123) → Get issue, view attachment list
2. get_attachment_info(456) → Confirm attachment information
3. get_attachment_image(456) → AI visual analysis of image content
```

### Feature Highlights
- **Thumbnail Mode**: Enabled by default, scales large images down to 800px, significantly reducing token consumption
- **Format Conversion**: Automatically converts to JPEG format, optimizing file size
- **Transparency Handling**: PNG transparent backgrounds are automatically converted to white
- **Error Handling**: Non-image types, oversized files, etc. return friendly messages

### Supported Image Formats
- PNG (`image/png`)
- JPEG (`image/jpeg`)
- GIF (`image/gif`)
- WebP (`image/webp`)

### Limitations
- File size limit: 10 MB
- Default thumbnail size: 800 px (max edge length)

## Time Entry Feature ✨

### add_issue_note Time Entry Support
Now you can record work time while adding issue notes:

```python
# Add note and record time (using activity name)
add_issue_note(
    issue_id=1,
    notes="Feature development completed",
    spent_hours=2.5,
    activity_name="Development"
)

# Add note and record time (using activity ID)
add_issue_note(
    issue_id=1,
    notes="Bug fix",
    spent_hours=1.0,
    activity_id=12,
    spent_on="2025-06-25"  # Specify record date
)

# Private note + time entry
add_issue_note(
    issue_id=1,
    notes="Internal discussion record",
    private=True,
    spent_hours=0.5,
    activity_name="Discussion"
)

# Add note only (backward compatible)
add_issue_note(issue_id=1, notes="General note")
```

### Time Tracking Activity Support
The system supports the following default activities:
- Design (ID: 10)
- Development (ID: 11)
- Debug (ID: 12)
- Investigation (ID: 13)
- Discussion (ID: 14)
- Testing (ID: 15)
- Maintenance (ID: 16)
- Documentation (ID: 17)
- Teaching (ID: 18)
- Translation (ID: 19)
- Other (ID: 20)

### Feature Highlights
- **Smart Cache**: Time tracking activity information is automatically cached to improve query efficiency
- **Name Parameters**: Supports using activity names instead of IDs for more intuitive usage
- **Backward Compatible**: Maintains full backward compatibility with the original `add_issue_note` function
- **Error Prompts**: Automatically displays available options when an invalid activity name is provided
- **Flexible Dates**: Can specify record date, defaults to today

## Notes

- The project is in the early development stage
- This file will be updated as development progresses
