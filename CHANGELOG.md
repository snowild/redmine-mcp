# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - Upcoming

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
