"""
Configuration management module tests
"""

import os
import pytest
from unittest.mock import patch
from redmine_mcp.config import RedmineConfig, get_config, reload_config


class TestRedmineConfig:
    """RedmineConfig class tests"""
    
    def test_config_with_valid_env(self):
        """Test configuration with valid environment variables"""
        reload_config()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key_123',
            'REDMINE_MCP_TIMEOUT': '45',
            'REDMINE_MCP_LOG_LEVEL': 'DEBUG'
        }):
            config = RedmineConfig()
            
            assert config.redmine_domain == 'https://test.redmine.com'
            assert config.redmine_api_key == 'test_api_key_123'
            assert config.redmine_timeout == 45
            assert config.debug_mode is True
    
    def test_config_missing_required_env(self):
        """Test missing required environment variables"""
        reload_config()
        with patch.dict(os.environ, {'REDMINE_DOMAIN': '', 'REDMINE_API_KEY': ''}):
            with patch('redmine_mcp.config.load_dotenv'):
                with pytest.raises(ValueError, match="Required environment variable REDMINE_DOMAIN is not set"):
                    RedmineConfig()
    
    def test_config_invalid_domain(self):
        """Test invalid domain format"""
        reload_config()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'invalid-domain',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            with pytest.raises(ValueError, match="REDMINE_DOMAIN must start with http:// or https://"):
                RedmineConfig()
    
    def test_config_domain_trailing_slash_removal(self):
        """Test removal of trailing slash from domain"""
        reload_config()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com/',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            config = RedmineConfig()
            assert config.redmine_domain == 'https://test.redmine.com'
    
    def test_config_default_values(self):
        """Test default values"""
        reload_config()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            config = RedmineConfig()
            
            assert config.redmine_timeout == 30  # Default value
            assert config.debug_mode is False   # Default value
    
    def test_api_headers(self):
        """Test API header generation"""
        reload_config()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key_123'
        }):
            config = RedmineConfig()
            headers = config.api_headers
            
            assert headers['X-Redmine-API-Key'] == 'test_api_key_123'
            assert headers['Content-Type'] == 'application/json'
    
    def test_config_repr(self):
        """Test string representation does not contain sensitive information"""
        reload_config()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'secret_api_key'
        }):
            config = RedmineConfig()
            repr_str = repr(config)
            
            assert 'https://test.redmine.com' in repr_str
            assert 'secret_api_key' not in repr_str  # Sensitive information should be hidden


class TestConfigSingleton:
    """Test configuration singleton pattern"""
    
    def test_get_config_singleton(self):
        """Test get_config returns the same instance"""
        reload_config()
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            config1 = get_config()
            config2 = get_config()
            
            assert config1 is config2
    
    def test_reload_config(self):
        """Test reload_config creates a new instance"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }):
            reload_config()
            config1 = get_config()
            reload_config()
            config2 = get_config()
            
            # Although it's a new instance, the content should be the same
            assert config1 is not config2
            assert config1.redmine_domain == config2.redmine_domain
