"""
配置管理模組
負責載入和驗證環境變數配置
"""

import os
from typing import Optional
from dotenv import load_dotenv


class RedmineConfig:
    """Redmine MCP 服務器配置管理"""
    
    def __init__(self):
        # 載入環境變數
        load_dotenv()
        
        # 必要配置
        self.redmine_domain = self._get_required_env("REDMINE_DOMAIN")
        self.redmine_api_key = self._get_required_env("REDMINE_API_KEY")
        
        # 可選配置 - 使用專屬前綴避免與其他專案環境變數衝突
        self.redmine_timeout = int(os.getenv("REDMINE_MCP_TIMEOUT") or os.getenv("REDMINE_TIMEOUT") or "30")

        # SSE 傳輸配置
        self.transport = os.getenv("REDMINE_MCP_TRANSPORT", "stdio").lower()
        self.sse_host = os.getenv("REDMINE_MCP_HOST", "0.0.0.0")
        self.sse_port = int(os.getenv("REDMINE_MCP_PORT", "8000"))
        
        # 日誌級別管理策略：
        # 1. 優先使用 REDMINE_MCP_LOG_LEVEL（專屬變數）
        # 2. 其次使用 LOG_LEVEL（向後相容）
        # 3. 都沒設定時預設為 INFO
        # 4. FASTMCP_LOG_LEVEL 始終跟隨最終的日誌級別值
        redmine_log_level = os.getenv("REDMINE_MCP_LOG_LEVEL")
        if redmine_log_level:
            self.log_level = redmine_log_level.upper()
        else:
            # 向後相容：如果沒有專屬變數，檢查舊的 LOG_LEVEL
            legacy_log_level = os.getenv("LOG_LEVEL")
            if legacy_log_level:
                self.log_level = legacy_log_level.upper()
            else:
                self.log_level = "INFO"
        
        # FastMCP 日誌級別控制 - 始終設定為與最終日誌級別相同的值
        # 無論使用者是否有設定 FASTMCP_LOG_LEVEL，都會被覆蓋
        os.environ["FASTMCP_LOG_LEVEL"] = self.log_level
        self.fastmcp_log_level = self.log_level
        
        self.effective_log_level = self.log_level
        self.debug_mode = self.effective_log_level == "DEBUG"
        
        self._validate_config()
    
    def _get_required_env(self, key: str) -> str:
        """取得必要的環境變數，如果不存在則拋出錯誤"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"必要的環境變數 {key} 未設定")
        return value
    
    def _validate_config(self) -> None:
        """驗證配置的有效性"""
        # 驗證 domain 格式
        if not self.redmine_domain.startswith(('http://', 'https://')):
            raise ValueError("REDMINE_DOMAIN 必須以 http:// 或 https:// 開頭")
        
        # 移除末尾的斜線
        self.redmine_domain = self.redmine_domain.rstrip('/')
        
        # 驗證 API key 不為空
        if not self.redmine_api_key.strip():
            raise ValueError("REDMINE_API_KEY 不能為空")
        
        # 驗證 timeout 值
        if self.redmine_timeout <= 0:
            raise ValueError("REDMINE_TIMEOUT 必須大於 0")
        
        # 驗證 log_level 值
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_levels:
            raise ValueError(f"日誌級別必須是以下值之一: {', '.join(valid_levels)}（當前: {self.log_level}）")

        # 驗證 transport 值
        valid_transports = ['stdio', 'sse']
        if self.transport not in valid_transports:
            raise ValueError(f"傳輸模式必須是以下值之一: {', '.join(valid_transports)}（當前: {self.transport}）")

        # 驗證 SSE port 值
        if self.sse_port <= 0 or self.sse_port > 65535:
            raise ValueError(f"SSE 埠號必須在 1-65535 之間（當前: {self.sse_port}）")
    
    @property
    def api_headers(self) -> dict[str, str]:
        """回傳 API 請求所需的標頭"""
        return {
            'X-Redmine-API-Key': self.redmine_api_key,
            'Content-Type': 'application/json'
        }
    
    def __repr__(self) -> str:
        """除錯用的字串表示，隱藏敏感資訊"""
        return f"RedmineConfig(domain='{self.redmine_domain}', timeout={self.redmine_timeout}, transport='{self.transport}', sse_host='{self.sse_host}', sse_port={self.sse_port}, log_level='{self.log_level}', debug={self.debug_mode})"


# 全域配置實例
_config: Optional[RedmineConfig] = None


def get_config() -> RedmineConfig:
    """取得全域配置實例（單例模式）"""
    global _config
    if _config is None:
        _config = RedmineConfig()
    return _config


def reload_config() -> RedmineConfig:
    """重新載入配置（主要用於測試）"""
    global _config
    _config = None
    return get_config()