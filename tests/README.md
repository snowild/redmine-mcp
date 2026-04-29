# Test Directory Structure Guide

This directory contains all test files for the redmine-mcp project, organized into three main categories:

## 📁 Directory Structure

```
tests/
├── unit/              # Unit tests (pytest)
│   ├── test_config.py         # Configuration management tests
│   ├── test_redmine_client.py # Redmine client tests
│   └── test_validators.py     # Data validation tests
├── integration/       # Integration tests (pytest)
│   ├── test_mcp_tools.py          # MCP tool integration tests
│   └── test_advanced_mcp_tools.py # Advanced MCP tool tests
└── scripts/          # Test scripts (run directly)
    ├── claude_integration.py # Claude Code integration test
    ├── claude_setup.py       # Claude Code setup test
    ├── installation.py       # Package installation test
    └── mcp_integration.py    # Complete MCP functionality test
```

## 🧪 Test Types

### Unit Tests
- **Purpose**: Test functionality of individual modules and functions
- **Characteristics**: Independent, fast, repeatable
- **Framework**: pytest
- **Run**: `uv run python -m pytest tests/unit/`

### Integration Tests
- **Purpose**: Test interactions between different modules
- **Characteristics**: Requires external services (e.g., Redmine)
- **Framework**: pytest + mock
- **Run**: `uv run python -m pytest tests/integration/`

### Test Scripts
- **Purpose**: End-to-end functionality verification and environment setup
- **Characteristics**: Run independently, includes setup logic
- **Framework**: Native Python
- **Run**: `uv run python tests/scripts/<script_name>.py`

## 🚀 Quick Start

### Run All Tests
```bash
# Run all pytest tests
uv run python -m pytest tests/

# Run complete functionality tests
uv run python tests/scripts/mcp_integration.py
```

### Run Specific Test Types
```bash
# Run only unit tests
uv run python -m pytest tests/unit/

# Run only integration tests
uv run python -m pytest tests/integration/

# Test Claude Code integration
uv run python tests/scripts/claude_integration.py

# Test package installation
uv run python tests/scripts/installation.py
```

### Development Testing Workflow
```bash
# 1. After modifying code, run unit tests first
uv run python -m pytest tests/unit/ -v

# 2. If passed, run integration tests
uv run python -m pytest tests/integration/ -v

# 3. Finally run complete functionality tests
uv run python tests/scripts/mcp_integration.py
```

## 📝 Test File Descriptions

### Unit Test Files

#### `test_config.py`
- Tests configuration management module (`config.py`)
- Validates environment variable reading and validation logic
- Tests new dedicated environment variable mechanism

#### `test_redmine_client.py`
- Tests Redmine API client (`redmine_client.py`)
- Mock HTTP requests and responses
- Validates error handling mechanisms

#### `test_validators.py`
- Tests data validators (`validators.py`)
- Validates input data format and range checking
- Tests error message generation

### Integration Test Files

#### `test_mcp_tools.py`
- Tests basic functionality of MCP tools
- Simulates Redmine service responses
- Validates data flow between tools

#### `test_advanced_mcp_tools.py`
- Tests advanced MCP tool functionality
- Complex scenarios and boundary condition tests
- Performance and stability validation

### Test Script Files

#### `claude_integration.py`
- Tests integration with Claude Code
- Validates MCP server executability
- Checks tool registration and availability

#### `claude_setup.py`
- Tests Claude Code MCP configuration
- Validates configuration file generation
- Tests environment variable settings

#### `installation.py`
- Tests package installation and import
- Validates command line tool availability
- Checks dependencies

#### `mcp_integration.py`
- Complete end-to-end functionality test
- Requires a running Redmine service
- Tests all 14 MCP tools

## 🔧 Environment Requirements

### Unit Tests
- Python 3.12+
- pytest
- Related mock packages

### Integration Tests
- All unit test requirements
- Optional Redmine service (not needed when using mock)

### Test Scripts
- Complete development environment
- Docker and Docker Compose (for Redmine service)
- Network connection (for Claude Code integration tests)

## 📊 Test Coverage

Use pytest-cov to check test coverage:

```bash
# Install coverage tool
uv add --dev pytest-cov

# Run tests and generate coverage report
uv run python -m pytest tests/ --cov=src/redmine_mcp --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🐛 Troubleshooting

### Common Problems

**Q: pytest cannot find modules**
```bash
# Ensure running from project root directory
cd /path/to/redmine-mcp
uv run python -m pytest tests/
```

**Q: Integration tests fail**
- Check if Redmine service needs to be started
- Confirm network connection and API key settings

**Q: Test script execution errors**
- Check if import paths are correct
- Confirm all dependencies are installed

### Debug Techniques

```bash
# Run specific test file
uv run python -m pytest tests/unit/test_config.py -v

# Run specific test function
uv run python -m pytest tests/unit/test_config.py::TestRedmineConfig::test_config_with_valid_env -v

# Show detailed output
uv run python -m pytest tests/ -v -s

# Stop at first failure
uv run python -m pytest tests/ -x
```

## 🚀 Continuous Integration

In CI/CD workflows, the recommended execution order is:

1. **Quick Check**: Unit tests
2. **Deep Validation**: Integration tests
3. **Final Confirmation**: Key test scripts

```bash
# CI workflow example
uv run python -m pytest tests/unit/ --maxfail=5
uv run python -m pytest tests/integration/ --maxfail=3
uv run python tests/scripts/installation.py
```
