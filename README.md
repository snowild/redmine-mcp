# Redmine MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Redmine integration, enabling Claude Code to directly interact with Redmine project management systems.

## 🚀 Features

### ✅ Issue Management
- **Query Issues**: Get detailed issue information and lists
- **Create Issues**: Create new issues and set related attributes
- **Update Issues**: Modify issue content, status, priority, etc.
- **Assign Issues**: Assign or unassign issues to specific users
- **Add Notes**: Add public or private notes to issues
- **Close Issues**: Automatically set issues to completed status

### ✅ Project Management
- **Project Lists**: Get accessible project lists
- **Project Issues**: Filter by status and list all issues in projects

### ✅ Search Features
- **Keyword Search**: Search for keywords in issue titles and descriptions
- **My Issues**: Quick view of issues assigned to current user

### ✅ System Tools
- **Health Check**: Verify MCP server and Redmine connection status
- **Status Query**: Get available issue status lists

## 📋 System Requirements

- **Python**: 3.12 or higher
- **Redmine**: Version with REST API support (recommended 4.0+)
- **Package Manager**: [uv](https://docs.astral.sh/uv/) or pip

## 🔧 Installation & Setup

### 1. Clone the Project

```bash
git clone https://github.com/snowild/redmine-mcp.git
cd redmine-mcp
```

### 2. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

### 3. Environment Configuration

Create a `.env` file:
```bash
cp .env.example .env
```

Edit the `.env` file and set the following environment variables:
```env
REDMINE_DOMAIN=https://your-redmine-domain.com
REDMINE_API_KEY=your_api_key_here

# Project-specific variables (avoid conflicts with other projects)
REDMINE_MCP_LOG_LEVEL=INFO
REDMINE_MCP_TIMEOUT=30

# Backward compatibility variables (fallback)
REDMINE_TIMEOUT=30
LOG_LEVEL=info
```

#### Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REDMINE_DOMAIN` | Redmine server URL | *Required* | `https://redmine.example.com` |
| `REDMINE_API_KEY` | Your Redmine API key | *Required* | `abc123...` |
| `REDMINE_MCP_LOG_LEVEL` | Log level for this MCP server | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `REDMINE_MCP_TIMEOUT` | Request timeout (seconds) | `30` | `60` |
| `REDMINE_MCP_TRANSPORT` | Transport mode | `stdio` | `stdio`, `sse` |
| `REDMINE_MCP_HOST` | SSE bind address | `0.0.0.0` | `127.0.0.1` |
| `REDMINE_MCP_PORT` | SSE listen port | `8000` | `3000` |
| `LOG_LEVEL` | Legacy log level (backward compatibility) | - | `debug`, `info` |
| `REDMINE_TIMEOUT` | Legacy timeout (backward compatibility) | - | `30` |

**Log Level Priority:**
1. `REDMINE_MCP_LOG_LEVEL` (highest priority - project-specific)
2. `LOG_LEVEL` (backward compatibility)
3. `INFO` (default if neither is set)

> **Note**: The system automatically handles case conversion and ensures FastMCP compatibility.

### 4. Multi-User Support (Optional)

The server supports named user profiles, allowing multiple agents/users to operate as different Redmine identities within a single MCP configuration.

#### 4.1 Create User Profiles File

Create `~/.redmine_mcp/users.json`:

```json
{
  "alice": {
    "api_key": "alice_redmine_api_key",
    "description": "Project Manager"
  },
  "bob": {
    "api_key": "bob_redmine_api_key",
    "description": "Developer"
  }
}
```

Or use the simple string format:
```json
{
  "alice": "alice_redmine_api_key",
  "bob": "bob_redmine_api_key"
}
```

#### 4.2 Using Profiles

All MCP tools accept an optional `profile_name` parameter:

```python
# Act as alice
get_issue(123, profile_name="alice")

# Act as bob
create_new_issue(project_id=1, subject="Bug fix", profile_name="bob")
```

If `profile_name` is omitted, the default `REDMINE_API_KEY` from `.env` is used.

Use `list_user_profiles()` to see available profiles.

> **Security Note**: Raw API keys are never exposed in tool arguments. Only pre-configured profile names are passed.

#### Setting a Default User (Recommended)

Instead of passing `profile_name` on every call, set a default user once per session:

```python
# 1. List available profiles
list_user_profiles()

# 2. Set yourself as the current user
set_current_user(profile_name="Семён Слепоков")

# 3. Now all calls use Семён's API key automatically
get_issue(123)
add_issue_note(issue_id=123, notes="Done")
create_new_issue(project_id=1, subject="New task")

# 4. Override for a single call if needed
get_issue(456, profile_name="Валентина Петрова")

# 5. Clear the default
set_current_user(profile_name="")
```

You can also set a default profile via environment variable:
```env
REDMINE_DEFAULT_PROFILE=Семён Слепоков
```

> **Important for SSE mode**: `set_current_user` sets the default for the entire server process. If multiple agents connect to the same SSE server, they share the same default. For isolated sessions use stdio mode or run separate containers per user.

#### Docker / Docker Compose

When running in a container, mount the `users.json` file:

```bash
# Docker run
docker run -d \
  -e REDMINE_DOMAIN=https://your-redmine.com \
  -e REDMINE_API_KEY=your_api_key \
  -v $(pwd)/users.json:/home/mcp/.redmine_mcp/users.json:ro \
  -p 8000:8000 \
  --name redmine-mcp \
  redmine-mcp
```

For Docker Compose, the `docker-compose.yml` already includes the volume mount. Just create `users.json` next to `docker-compose.yml`:

```bash
echo '{"alice": "alice_api_key", "bob": "bob_api_key"}' > users.json
docker compose up -d
```

### 5. Redmine API Setup

#### 5.1 Enable REST API
1. Log in to Redmine as administrator
2. Go to **Administration** → **Settings** → **API**
3. Check **"Enable REST web service"**
4. Click **Save**

#### 5.2 Configure Redmine Basic Data (Administrator)
Before using MCP tools, you need to configure Redmine's basic data:

**Configure Roles and Permissions**
1. Go to **Administration** → **Roles and permissions**
2. Create or edit roles (e.g.: Developer, Tester, Project Manager)
3. Assign appropriate permissions to roles (recommend at least: View issues, Add issues, Edit issues)

**Configure Trackers**
1. Go to **Administration** → **Trackers**
2. Create tracker types (e.g.: Bug, Feature, Support)
3. Set default status and workflow for each tracker

**Configure Issue Statuses**
1. Go to **Administration** → **Issue statuses**
2. Create statuses (e.g.: New, In Progress, Resolved, Closed, Rejected)
3. Set status attributes (whether it's a closed status, etc.)

**Configure Workflow**
1. Go to **Administration** → **Workflow**
2. Set allowed status transitions for each role and tracker combination
3. Ensure basic status transition paths (New → In Progress → Resolved → Closed)

**Create Projects**
1. Go to **Projects** → **New project**
2. Set project name, identifier, description
3. Select enabled modules (at least enable "Issue tracking")
4. Assign members and set roles

#### 5.3 Get API Key
1. Log in to your Redmine system (can be administrator or regular user)
2. Go to **My account** → **API access key**
3. Click **Show** or **Reset** to get the API key
4. Copy the key to `REDMINE_API_KEY` in the `.env` file

> **⚠️ Important Notes**: 
> - If you can't find the API key option, please ensure step 4.1 (Enable REST API) is completed
> - Complete basic setup before you can properly create and manage issues
> 
> **📚 Detailed Setup Guide**: For complete Redmine setup steps, please refer to [Redmine Complete Setup Guide](docs/manuals/redmine_setup_guide.md)

## 💬 Usage Examples in Chat

### Acting as a Specific User

**Recommended approach**: set the current user once, then work normally.

```python
# 1. List available profiles
list_user_profiles()
# → Available user profiles:
#   - alice - Project Manager
#   - bob - Developer

# 2. Set yourself as the current user (one time per session)
set_current_user(profile_name="alice")

# 3. All subsequent calls automatically use alice's API key
get_issue(123)
create_new_issue(project_id=1, subject="[Bug] Login error")
update_issue_status(issue_id=123, status_name="Resolved")
get_my_issues(status_filter="open")

# 4. Override for a single call if needed
get_issue(456, profile_name="bob")

# 5. Clear when done
set_current_user(profile_name="")
```

**Alternative**: pass `profile_name` explicitly on every call (useful for one-off actions):

```python
get_issue(123, profile_name="alice")
add_issue_note(issue_id=123, notes="Done", profile_name="bob")
```

> **Note**: `set_current_user` stores the default in the server's memory. In SSE mode with multiple agents sharing one server, they share the same default. For fully isolated sessions, use stdio mode or run separate containers.

## 🔗 Claude Code Integration

### Install to Claude Code

```bash
# Install from local
uv tool install .

# Or using pip
pip install .

# Add to Claude Code MCP configuration
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here"
```

### Verify Installation

```bash
# Test MCP server
uv run python -m redmine_mcp.server

# Test Claude Code integration
uv run python tests/scripts/claude_integration.py
```

## 🌐 SSE Mode & Docker Deployment

### Transport Modes

Redmine MCP supports two transport modes:

| Mode | Use Case | Multi-Client | Deployment |
|------|----------|--------------|------------|
| **stdio** (default) | Local CLI usage with Claude Code | ❌ Single | Auto-started by Claude Code |
| **sse** | Team sharing, remote access, containerized | ✅ Multiple | Manual start required |

### Running in SSE Mode

#### Quick Start (Development)

```bash
# Navigate to project directory (where .env file is located)
cd /path/to/redmine-mcp

# Run with uv (reads .env automatically)
uv run redmine-mcp --transport sse

# Custom host and port
uv run redmine-mcp --transport sse --host 127.0.0.1 --port 3000
```

#### Global Installation

```bash
# Install globally
uv tool install . --force --reinstall

# Set environment variables
export REDMINE_DOMAIN=https://your-redmine.com
export REDMINE_API_KEY=your_api_key_here

# Run from anywhere
redmine-mcp --transport sse
```

#### Using .env File

Create a `.env` file in your working directory:
```env
REDMINE_DOMAIN=https://your-redmine.com
REDMINE_API_KEY=your_api_key_here
REDMINE_MCP_TRANSPORT=sse
REDMINE_MCP_PORT=8000
```

> **Note**: `uv run` automatically loads `.env` from the project directory. Global installation requires explicit environment variables or running from the directory containing `.env`.

### Docker Deployment

#### Quick Start with Docker

```bash
# Build the image
docker build -t redmine-mcp .

# Run with environment variables
docker run -d \
  -e REDMINE_DOMAIN=https://your-redmine.com \
  -e REDMINE_API_KEY=your_api_key \
  -p 8000:8000 \
  --name redmine-mcp \
  redmine-mcp
```

#### Using Docker Compose

```bash
# Edit docker-compose.yml with your Redmine settings
# Then start the service
docker compose up -d

# View logs
docker compose logs -f

# Stop the service
docker compose down
```

#### Docker with Multi-User Profiles

```yaml
# docker-compose.yml
services:
  redmine-mcp:
    build: .
    container_name: redmine-mcp
    ports:
      - "8000:8000"
    environment:
      - REDMINE_DOMAIN=${REDMINE_DOMAIN}
      - REDMINE_API_KEY=${REDMINE_API_KEY}
    volumes:
      - ./users.json:/home/mcp/.redmine_mcp/users.json:ro
    restart: unless-stopped
```
```

#### Docker Compose with .env file (Recommended)

1. Create `.env` file:
```env
REDMINE_DOMAIN=https://your-redmine.com
REDMINE_API_KEY=your_api_key_here
```

2. Update `docker-compose.yml` to use environment variables:
```yaml
environment:
  - REDMINE_DOMAIN=${REDMINE_DOMAIN}
  - REDMINE_API_KEY=${REDMINE_API_KEY}
```

3. Start the service:
```bash
docker compose up -d
```

### Connecting Claude Code to SSE Server

Once the SSE server is running, configure Claude Code to connect:

```bash
# Add MCP with SSE transport
claude mcp add --transport sse redmine http://localhost:8000/sse
```

Or manually edit `~/.claude.json`:

```json
{
  "mcpServers": {
    "redmine": {
      "transport": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

> **Note**: Environment variables (`REDMINE_DOMAIN`, `REDMINE_API_KEY`) are configured on the **SSE server side**, not in Claude Code.

### Connecting VS Code (GitHub Copilot) to SSE Server

VS Code with GitHub Copilot can also connect to the SSE server. Edit the MCP configuration file:

**macOS**: `~/Library/Application Support/Code/User/mcp.json`

**Windows**: `%APPDATA%\Code\User\mcp.json`

**Linux**: `~/.config/Code/User/mcp.json`

Add the following configuration:

```json
{
  "servers": {
    "redmine": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

> **Reference**: For more details on VS Code MCP configuration, see [VS Code MCP Servers Documentation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers).

## 🔄 Updating/Reinstalling MCP

If you need to update to the latest version of the MCP server or reinstall it:

### Quick Update (Recommended)

```bash
# Navigate to project directory
cd /path/to/redmine-mcp

# Pull latest changes (if from git)
git pull origin main

# Force reinstall with uv tool
uv tool install . --force --reinstall

# Restart Claude Code to reload MCP server
```

### Full Reinstallation

If quick update doesn't work, follow these steps:

#### 1. Remove Previous Installation

```bash
# Remove from Claude Code
claude mcp remove redmine

# Uninstall the package (if installed with uv tool)
uv tool uninstall redmine-mcp

# Or if installed with pip
pip uninstall redmine-mcp
```

#### 2. Install Latest Version

```bash
# Navigate to project directory
cd /path/to/redmine-mcp

# Pull latest changes (if from git)
git pull origin main

# Install latest version
uv tool install .

# Or using pip
pip install .
```

#### 3. Re-register with Claude Code

```bash
# Use full path to avoid PATH conflicts
claude mcp add redmine "$(which redmine-mcp)" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here" \
  -e REDMINE_MCP_LOG_LEVEL="INFO" \
  -e REDMINE_MCP_TIMEOUT="30"
```

#### 4. Verify Updated Installation

```bash
# Check installed version
uv tool list | grep redmine

# Verify MCP registration
claude mcp list

# Or check in Claude Code using slash command
# /mcp
```

### Troubleshooting Update Issues

**Problem: Old version still running after update**
- This usually happens when PATH has multiple `redmine-mcp` executables
- Solution: Use full path in Claude Code MCP config

```bash
# Find the correct path
ls -la ~/.local/bin/redmine-mcp

# Update MCP config with full path
claude mcp remove redmine
claude mcp add redmine "/Users/YOUR_USERNAME/.local/bin/redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here"
```

**Problem: "Failed to reconnect to redmine" after update**
- Restart Claude Code completely (close and reopen)
- Or use `/mcp` command and select `restart` for redmine server

> **Important Notes:**
> - Always restart Claude Code after updating MCP server
> - Use `--force --reinstall` flags to ensure clean installation
> - Check tool count in `/mcp` to verify update (current: 26 tools)

## 🛠️ Available MCP Tools (26 tools)

### Basic Tools
| Tool Name | Description |
|-----------|-------------|
| `server_info` | Display server information and configuration status |
| `health_check` | Check server and Redmine connection health status |
| `refresh_cache` | Manually refresh enum values and user cache |

### Issue Operations
| Tool Name | Description |
|-----------|-------------|
| `get_issue` | Get detailed information of specified issue |
| `create_new_issue` | Create a new issue (supports name parameters) |
| `update_issue_status` | Update issue status |
| `update_issue_content` | Update issue content (title, description, etc.) |
| `add_issue_note` | Add notes to issues (supports time tracking) |
| `assign_issue` | Assign or unassign issues |
| `close_issue` | Close issue and set completion rate |

### Journal Tools
| Tool Name | Description |
|-----------|-------------|
| `list_issue_journals` | List all journals/notes for an issue |
| `get_journal` | Get detailed information of a specific journal |

### Attachment Tools ✨ New
| Tool Name | Description |
|-----------|-------------|
| `get_attachment_info` | Get attachment metadata (without downloading) |
| `get_attachment_image` | Download image for AI visual analysis (supports thumbnail) |

### Query Tools
| Tool Name | Description |
|-----------|-------------|
| `list_project_issues` | List issues in projects |
| `get_my_issues` | Get list of issues assigned to me |
| `search_issues` | Search for issues containing keywords |
| `get_projects` | Get list of accessible projects |
| `get_issue_statuses` | Get all available issue statuses |
| `get_trackers` | Get all available tracker lists |
| `get_priorities` | Get all available issue priorities |
| `get_time_entry_activities` | Get all available time tracking activities |
| `get_document_categories` | Get all available document categories |

### User Tools
| Tool Name | Description |
|-----------|-------------|
| `search_users` | Search users by name or login |
| `list_users` | List all users |
| `get_user` | Get detailed information of a specific user |

## 💡 Usage Examples

### Using in Claude Code

```
# Check server status
Please run health check

# Get project list
Show all accessible projects

# View system settings
Get all available issue statuses
Get all available tracker lists
Get all available issue priorities
Get all available time tracking activities
Get all available document categories

# View specific issue
Get detailed information for issue #123

# Create new issue
Create an issue in project ID 1:
- Title: Fix login error
- Description: Users cannot log in to the system properly
- Priority: High

# Search issues
Search for issues containing "login" keyword

# Update issue status
Update issue #123 status to "In Progress" with note "Starting to handle this issue"
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
uv run python -m pytest

# Run MCP integration tests
uv run python tests/scripts/mcp_integration.py

# Run Claude Code integration tests  
uv run python tests/scripts/claude_integration.py
```

### Docker Environment Testing

If you want to test in a local Docker environment:

```bash
# Start Redmine test environment
docker-compose up -d

# Quick start complete test environment
./quick_start.sh
```

## 📁 Project Structure

```
redmine-mcp/
├── src/redmine_mcp/          # Main source code
│   ├── __init__.py           # Package initialization
│   ├── server.py             # MCP server main program
│   ├── redmine_client.py     # Redmine API client
│   ├── config.py             # Configuration management
│   └── validators.py         # Data validation
├── tests/                    # Test files
├── docs/                     # Documentation directory
├── Dockerfile                # Docker build configuration
├── docker-compose.yml        # Docker Compose configuration
├── .dockerignore             # Docker build exclusions
├── CHANGELOG.md              # Version history
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

## 🤝 Contributing

1. Fork this project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📦 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## 🔗 Related Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code](https://claude.ai/code)
- [Redmine](https://www.redmine.org/)
- [FastMCP](https://github.com/jlowin/fastmcp)

---

If you have any questions or suggestions, feel free to open an Issue or contact the project maintainers.