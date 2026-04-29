# Version Management Guide

This document explains how to manage version numbers in the Redmine MCP project.

## 📍 Version Configuration Locations

### Primary Version Source
- **`pyproject.toml`** - The **single source of truth** for package version
  ```toml
  [project]
  version = "0.1.0"
  ```

### Dynamic Version Reading
- **`src/redmine_mcp/__init__.py`** - Automatically reads version from `pyproject.toml`
  ```python
  try:
      from importlib.metadata import version
      __version__ = version("redmine-mcp")
  except ImportError:
      __version__ = "0.1.0"  # fallback
  ```

## 🔄 Version Release Process

### 1. Update Version Number
```bash
# Edit the version number in pyproject.toml
version = "0.2.0"
```

### 2. Update CHANGELOG.md
```markdown
## [0.2.0] - 2024-12-XX

### Added
- New feature description

### Changed
- Change description

### Fixed
- Bug fix description
```

### 3. Verify Version
```bash
# Check if version is read correctly
uv run python -c "import redmine_mcp; print(redmine_mcp.__version__)"
```

### 4. Commit Changes
```bash
git add pyproject.toml CHANGELOG.md
git commit -m "bump version to 0.2.0"
```

### 5. Create Tag
```bash
git tag v0.2.0
git push origin main --tags
```

### 6. Build and Publish (Optional)
```bash
# Build package
uv build

# Publish to PyPI (if needed)
uv publish
```

## 🎯 Version Number Specification

This project follows [Semantic Versioning](https://semver.org/) specification:

- **MAJOR version**: Incompatible API changes
- **MINOR version**: Backward-compatible functionality additions
- **PATCH version**: Backward-compatible bug fixes

Example: `1.2.3`
- `1` = Major version
- `2` = Minor version
- `3` = Patch version

## 📋 Version Management Checklist

Checklist before releasing a new version:

- [ ] Update version number in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with new version record
- [ ] Run tests to ensure functionality is normal: `uv run python -m pytest`
- [ ] Verify version reading: `uv run python -c "import redmine_mcp; print(redmine_mcp.__version__)"`
- [ ] Commit all changes
- [ ] Create Git tag
- [ ] Push to remote repository

## 🛠️ Common Commands

```bash
# View current version
uv run python -c "import redmine_mcp; print(redmine_mcp.__version__)"

# Check git tags
git tag -l

# View version history
git log --oneline --decorate --graph

# Compare version differences
git diff v0.1.0..v0.2.0
```

## ⚠️ Notes

1. **Single Source Principle**: Only set version number in `pyproject.toml`
2. **Auto Sync**: `__init__.py` automatically reads package version
3. **Development Environment**: Fallback version ensures functionality in development environment
4. **Tag Naming**: Git tags use `v` prefix (e.g., `v0.1.0`)
5. **Test Before Release**: Always run full tests before releasing

## 🔗 Related Resources

- [Semantic Versioning Specification](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Python Package Version Management](https://packaging.python.org/guides/single-sourcing-package-version/)
