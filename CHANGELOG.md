# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-03-09

### Added
- **Attachment Text Extraction**: `get_attachment_text` tool for reading PDF, Word, Excel, PPT, JSON, TXT, XML and other text-based attachments
- **Compound Tools**: `resolve_issue` for one-call issue resolution (status + done_ratio + custom_fields + notes + time logging), `start_working` for beginning work on issues (status + start_date + assign to self)
- **Change Detection**: `check_issue_changes` for detecting field changes via in-memory snapshots, `sync_my_issues` for batch change detection of assigned issues with project filtering
- **Project Sync**: `sync_project_issues` for full project issue sync with auto-pagination, tree structure output, and change detection markers
- **Issue Snapshot Mechanism**: Auto-saved on `get_issue_raw`, tracks status, priority, assigned_to, done_ratio, subject, description, journals_count, attachments_count, custom_fields
- **Category Cache**: On-demand per-project issue category cache with CRUD helpers (`get_issue_categories`, `find_category_id_by_name`, `refresh_category_cache`)
- **Watcher Management**: `add_watcher` and `remove_watcher` tools with name-based user resolution
- **Enhanced create_new_issue**: Added `parent_issue_id`, `start_date`, `due_date`, `estimated_hours`, `status_id`/`status_name`, `category_id`/`category_name` parameters
- **Enhanced update_issue_content**: Added `category_id`/`category_name` and `custom_fields` support

### Changed
- **get_issue output format**: Reformatted to Markdown table format aligned with team documentation standards
  - Emoji markers for tracker, status, priority
  - Field naming aligned with README (`Completion Percentage`, `Start Time`, `End Time`)
  - `@username` format for assignee
  - Dedicated rows for custom fields: `Actual End Date` (id=23), `Resolution Date` (id=64)
  - Status column added to children issue table

### Fixed
- **status_filter mapping**: Fixed `sync_project_issues` and `sync_my_issues` passing raw filter strings (`"open"`, `"all"`) instead of Redmine API values (`"o"`, `"*"`); now supports both formats

### Dependencies
- Added pypdf >= 4.0.0 for PDF text extraction
- Added python-docx >= 1.0.0 for Word document parsing
- Added openpyxl >= 3.1.0 for Excel spreadsheet parsing
- Added python-pptx >= 0.6.23 for PowerPoint presentation parsing

## [0.4.0] - 2025-01-14

### Added
- **SSE Transport Mode**: Support Server-Sent Events for remote access and multi-client connections
- **Docker Support**: Dockerfile and docker-compose.yml for containerized deployment
- **Command Line Arguments**: `--transport`, `--host`, `--port` options for flexible configuration
- **Attachment Image Analysis**: `get_attachment_image` tool for AI visual analysis of Redmine attachments
- **Thumbnail Mode**: Automatically resize large images to reduce token consumption (default: 800px max)
- **Attachment Info**: `get_attachment_info` tool to get attachment metadata without downloading
- New environment variables:
  - `REDMINE_MCP_TRANSPORT`: Transport mode (`stdio` or `sse`)
  - `REDMINE_MCP_HOST`: SSE bind address (default: `0.0.0.0`)
  - `REDMINE_MCP_PORT`: SSE listen port (default: `8000`)

### Changed
- Updated mcp[cli] to 1.25.0 for SSE host/port support

### Dependencies
- Added Pillow >= 10.0.0 for image processing

## [0.3.1] - 2025-01-01

### Fixed
- Bug fixes and stability improvements

### Changed
- Documentation updates

## [0.3.0] - 2024-12-15

### Added
- **Journal Tools**: `list_issue_journals`, `get_journal` for viewing issue notes and history
- **Time Tracking**: `add_issue_note` now supports time entry recording
- **Name Parameters**: Support using names instead of IDs for status, priority, tracker, and user
- Smart caching system for enum values and users
- Multi-domain cache support

### Improved
- Better error messages with available options

## [0.2.0] - 2024-12-01

### Added
- Initial public release
- Basic issue management (CRUD operations)
- Project and user queries
- Claude Code integration

## [0.1.0] - 2024-11-15

### Added
- Internal development version

[Unreleased]: https://github.com/snowild/redmine-mcp/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/snowild/redmine-mcp/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/snowild/redmine-mcp/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/snowild/redmine-mcp/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/snowild/redmine-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/snowild/redmine-mcp/releases/tag/v0.1.0
