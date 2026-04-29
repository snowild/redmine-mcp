"""
Configuration management module
Responsible for loading and validating environment variable configurations
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class RedmineConfig:
    """Redmine MCP server configuration management"""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Required configuration
        self.redmine_domain = self._get_required_env("REDMINE_DOMAIN")
        self.redmine_api_key = self._get_required_env("REDMINE_API_KEY")

        # User profiles configuration
        self._users_file_path = Path.home() / ".redmine_mcp" / "users.json"
        self._user_profiles: Optional[Dict[str, Dict[str, Any]]] = None
        self._default_profile_name: Optional[str] = os.getenv("REDMINE_DEFAULT_PROFILE") or None

        # Optional configuration - use dedicated prefix to avoid conflicts with other projects
        self.redmine_timeout = int(os.getenv("REDMINE_MCP_TIMEOUT") or os.getenv("REDMINE_TIMEOUT") or "30")

        # SSE transport configuration
        self.transport = os.getenv("REDMINE_MCP_TRANSPORT", "stdio").lower()
        self.sse_host = os.getenv("REDMINE_MCP_HOST", "0.0.0.0")
        self.sse_port = int(os.getenv("REDMINE_MCP_PORT", "8000"))

        # Log level management strategy:
        # 1. Prefer REDMINE_MCP_LOG_LEVEL (dedicated variable)
        # 2. Fall back to LOG_LEVEL (backward compatibility)
        # 3. Default to INFO if neither is set
        # 4. FASTMCP_LOG_LEVEL always follows the final log level value
        redmine_log_level = os.getenv("REDMINE_MCP_LOG_LEVEL")
        if redmine_log_level:
            self.log_level = redmine_log_level.upper()
        else:
            # Backward compatibility: check old LOG_LEVEL if dedicated variable is not set
            legacy_log_level = os.getenv("LOG_LEVEL")
            if legacy_log_level:
                self.log_level = legacy_log_level.upper()
            else:
                self.log_level = "INFO"

        # FastMCP log level control - always set to the same value as the final log level
        # Regardless of whether FASTMCP_LOG_LEVEL is set by the user, it will be overwritten
        os.environ["FASTMCP_LOG_LEVEL"] = self.log_level
        self.fastmcp_log_level = self.log_level

        self.effective_log_level = self.log_level
        self.debug_mode = self.effective_log_level == "DEBUG"

        self._validate_config()

    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable, raise an error if not set"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

    def _load_user_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load user profiles from the configuration file"""
        if self._user_profiles is not None:
            return self._user_profiles

        if not self._users_file_path.exists():
            self._user_profiles = {}
            return self._user_profiles

        try:
            with open(self._users_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Normalize to dict of dicts
            profiles: Dict[str, Dict[str, Any]] = {}
            for name, value in data.items():
                if isinstance(value, dict) and 'api_key' in value:
                    profiles[name] = {
                        'api_key': value['api_key'],
                        'description': value.get('description', '')
                    }
                elif isinstance(value, str):
                    # Simple string mapping: name -> api_key
                    profiles[name] = {'api_key': value, 'description': ''}
            self._user_profiles = profiles
        except (json.JSONDecodeError, OSError):
            self._user_profiles = {}

        return self._user_profiles

    def get_user_api_key(self, user_name: str) -> Optional[str]:
        """Get API key for a named user profile"""
        profiles = self._load_user_profiles()
        profile = profiles.get(user_name)
        if profile:
            return profile.get('api_key')
        return None

    def list_user_profiles(self) -> Dict[str, str]:
        """List available user profiles (name -> description, excluding API keys)"""
        profiles = self._load_user_profiles()
        return {
            name: profile.get('description', '')
            for name, profile in profiles.items()
        }

    def refresh_user_profiles(self) -> None:
        """Force reload user profiles from disk"""
        self._user_profiles = None

    @property
    def default_profile_name(self) -> Optional[str]:
        """Return the current default profile name (from env or set_current_user)"""
        return self._default_profile_name

    def set_default_profile(self, profile_name: Optional[str]) -> None:
        """Set the default profile name for this server instance"""
        self._default_profile_name = profile_name

    @property
    def users_file_path(self) -> Path:
        """Return the path to the user profiles file"""
        return self._users_file_path

    def _validate_config(self) -> None:
        """Validate configuration values"""
        # Validate domain format
        if not self.redmine_domain.startswith(("http://", "https://")):
            raise ValueError("REDMINE_DOMAIN must start with http:// or https://")

        # Remove trailing slash
        self.redmine_domain = self.redmine_domain.rstrip("/")

        # Validate API key is not empty
        if not self.redmine_api_key.strip():
            raise ValueError("REDMINE_API_KEY cannot be empty")

        # Validate timeout value
        if self.redmine_timeout <= 0:
            raise ValueError("REDMINE_TIMEOUT must be greater than 0")

        # Validate log_level value
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)} (current: {self.log_level})")

        # Validate transport value
        valid_transports = ["stdio", "sse"]
        if self.transport not in valid_transports:
            raise ValueError(f"Transport mode must be one of: {', '.join(valid_transports)} (current: {self.transport})")

        # Validate SSE port value
        if self.sse_port <= 0 or self.sse_port > 65535:
            raise ValueError(f"SSE port must be between 1-65535 (current: {self.sse_port})")

    @property
    def api_headers(self) -> dict[str, str]:
        """Return the headers required for API requests"""
        return {
            "X-Redmine-API-Key": self.redmine_api_key,
            "Content-Type": "application/json",
        }

    def __repr__(self) -> str:
        """Debug string representation, hides sensitive information"""
        return (
            f"RedmineConfig(domain='{self.redmine_domain}', timeout={self.redmine_timeout}, "
            f"transport='{self.transport}', sse_host='{self.sse_host}', sse_port={self.sse_port}, "
            f"log_level='{self.log_level}', debug={self.debug_mode})"
        )


# Global configuration instance
_config: Optional[RedmineConfig] = None


def get_config() -> RedmineConfig:
    """Get the global configuration instance (singleton)"""
    global _config
    if _config is None:
        _config = RedmineConfig()
    return _config


def reload_config() -> RedmineConfig:
    """Reload configuration (mainly used for testing)"""
    global _config
    _config = None
    return get_config()
