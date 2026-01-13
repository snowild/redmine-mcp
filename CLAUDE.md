# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個 MCP (Model Context Protocol) 伺服器專案，用於與 Redmine 系統整合。使用 Python 3.12+ 和 uv 包管理器。

## 開發環境設置

### 依賴管理
- 使用 `uv` 作為包管理器
- 安裝依賴：`uv sync`
- 執行測試：`uv run python -m pytest`

### 專案結構  
```
redmine-mcp/
├── src/redmine_mcp/          # 主要原始碼
│   ├── __init__.py           # 套件初始化
│   ├── server.py             # MCP 服務器主程式 ✓ 已完成
│   ├── redmine_client.py     # Redmine API 客戶端 ✓ 已完成
│   ├── config.py             # 配置管理 ✓ 已完成
├── tests/                    # 測試檔案
├── docs/                     # 文件目錄
│   ├── issues/               # 開發問題記錄
│   └── manuals/              # 技術手冊
├── pyproject.toml            # 專案配置和依賴
├── uv.lock                   # 鎖定的依賴版本
└── .env                      # 環境變數 (待建立)
```

## MCP 開發說明

### 技術棧
- **MCP SDK**: mcp[cli] >= 1.9.4 (使用 FastMCP)
- **HTTP 客戶端**: requests >= 2.31.0
- **配置管理**: python-dotenv >= 1.0.0
- **圖片處理**: Pillow >= 10.0.0
- **Python 版本**: >= 3.12

### MCP 服務器架構
- 使用 FastMCP 建立服務器
- 工具註冊使用 `@mcp.tool()` 裝飾器
- 支援非同步操作和類型安全

### Redmine API 整合
- **議題管理**: 查詢、建立、更新、刪除議題
- **專案管理**: 查詢、建立、更新、刪除、封存專案
- **用戶管理**: 查詢用戶、取得當前用戶資訊
- **元數據查詢**: 狀態、優先級、追蹤器列表
- **觀察者管理**: 新增/移除議題觀察者
- **完整篩選支援**: 多條件篩選和排序

## Claude Code 整合

### 安裝到 Claude Code
```bash
# 安裝 MCP 服務器
uv tool install .

# 或使用 pip
pip install .

# 添加到 Claude Code
claude mcp add redmine "redmine-mcp" \
  -e REDMINE_DOMAIN="https://your-redmine-domain.com" \
  -e REDMINE_API_KEY="your_api_key_here" \
  -e REDMINE_MCP_LOG_LEVEL="INFO" \
  -e REDMINE_MCP_TIMEOUT="30"
```

### 環境變數說明

為避免與其他專案的環境變數衝突，redmine-mcp 使用專屬前綴：

- **必要變數**：
  - `REDMINE_DOMAIN`: Redmine 伺服器網址
  - `REDMINE_API_KEY`: Redmine API 金鑰

- **日誌級別控制**：
  - `REDMINE_MCP_LOG_LEVEL`: 本專案專屬日誌級別（預設：INFO）
  - `FASTMCP_LOG_LEVEL`: FastMCP 內建變數（可選）
    - 如果不設定，系統會自動使用 `REDMINE_MCP_LOG_LEVEL` 的值
    - 設定此變數可單獨控制 FastMCP 的日誌輸出

- **其他配置**：
  - `REDMINE_MCP_TIMEOUT`: 請求超時時間（秒）
  - `REDMINE_TIMEOUT`: 向後相容的超時設定

### 可用的 MCP 工具（26 個）
- **管理工具**: server_info, health_check, refresh_cache
- **查詢工具**: get_issue, list_project_issues, get_projects, get_issue_statuses, get_trackers, get_priorities, get_time_entry_activities, get_document_categories, search_issues, get_my_issues
- **備註工具**: list_issue_journals, get_journal
- **附件工具**: get_attachment_info, get_attachment_image ✨ 新增（支援縮圖與視覺分析）
- **用戶工具**: search_users, list_users, get_user
- **編輯工具**: update_issue_status, update_issue_content, add_issue_note（支援時間記錄）, assign_issue, close_issue
- **建立工具**: create_new_issue（支援名稱參數）

## 常用指令

```bash
# 安裝依賴
uv sync

# 執行 MCP 服務器
uv run python -m redmine_mcp.server

# 測試 Claude Code 整合
uv run python tests/scripts/claude_integration.py

# 執行單元測試
uv run python -m pytest tests/unit/

# 執行所有測試
uv run python -m pytest tests/

# 添加新依賴
uv add <package-name>
```

## 智慧快取系統 ✨

### 快取機制特色
- **Multi-Domain 支援**: 根據 Redmine domain 自動建立獨立快取檔案
- **自動更新**: 24小時自動刷新快取資料
- **完整覆蓋**: 快取列舉值（優先權、狀態、追蹤器）和用戶資料
- **檔案位置**: `~/.redmine_mcp/cache_{domain}_{hash}.json`

### 可用的輔助函數
```python
client = get_client()

# 列舉值查詢
priority_id = client.find_priority_id_by_name("低")           # → 5
status_id = client.find_status_id_by_name("實作中")          # → 2  
tracker_id = client.find_tracker_id_by_name("臭蟲")         # → 1

# 用戶查詢
user_id = client.find_user_id("Redmine Admin")              # 智慧查詢（姓名或登入名）
user_id = client.find_user_id_by_name("Redmine Admin")      # 僅姓名查詢
user_id = client.find_user_id_by_login("admin")             # 僅登入名查詢

# 時間追蹤活動查詢
activity_id = client.find_time_entry_activity_id_by_name("開發")  # → 11

# 取得所有選項
priorities = client.get_available_priorities()              # {"低": 5, "正常": 6, ...}
users = client.get_available_users()                        # {"by_name": {...}, "by_login": {...}}
activities = client.get_available_time_entry_activities()   # {"設計": 10, "開發": 11, ...}

# 手動刷新
client.refresh_cache()
```

### MCP 工具
- `refresh_cache()`: 手動刷新快取並顯示統計資訊

## 名稱參數支援 ✨

### 支援名稱參數的 MCP 工具
以下工具現在支援使用名稱而不僅僅是 ID：

```python
# 更新議題狀態（使用名稱）
update_issue_status(issue_id=1, status_name="實作中")

# 更新議題內容（使用名稱）
update_issue_content(
    issue_id=1, 
    priority_name="高", 
    tracker_name="臭蟲"
)

# 指派議題（使用名稱）
assign_issue(issue_id=1, user_name="Redmine Admin")
assign_issue(issue_id=1, user_login="admin")

# 建立新議題（使用名稱）
create_new_issue(
    project_id=1,
    subject="新功能開發",
    priority_name="正常",
    tracker_name="功能",
    assigned_to_name="Redmine Admin"
)
```

### 錯誤處理
如果提供的名稱不存在，工具會自動顯示可用選項：
```
找不到優先級名稱：「超高」

可用優先級：
- 低
- 正常  
- 高
- 緊急
```

## 備註查詢功能 ✨

### 列出議題備註
使用 `list_issue_journals` 列出議題的所有備註記錄：

```python
# 列出有備註內容的記錄
list_issue_journals(issue_id=123)

# 包含屬性變更記錄（狀態、優先權等變更）
list_issue_journals(issue_id=123, include_property_changes=True)
```

輸出範例：
```
議題 #123 的備註記錄（共 3 筆）:
==================================================

📝 Journal #456
   作者: 張三
   時間: 2025-01-15T10:30:00Z
   備註內容:
      已完成初步測試

📝 Journal #457
   作者: 李四
   時間: 2025-01-16T14:20:00Z
   🔒 私有備註
   備註內容:
      內部討論記錄
```

### 取得單一備註詳情
使用 `get_journal` 取得特定備註的完整資訊：

```python
# 取得議題 #123 中的 Journal #456
get_journal(issue_id=123, journal_id=456)
```

輸出包含：
- Journal ID 和所屬議題
- 作者資訊（姓名和 ID）
- 建立時間
- 備註內容
- 屬性變更詳情（舊值 → 新值）

## 附件圖片視覺分析功能 ✨

### 取得附件資訊
使用 `get_attachment_info` 取得附件的詳細資訊（不下載檔案）：

```python
# 取得附件資訊
get_attachment_info(attachment_id=123)
```

輸出包含：檔案名稱、大小、類型、上傳者、上傳時間、下載連結

### 視覺分析圖片附件
使用 `get_attachment_image` 下載圖片並供 AI 進行視覺分析：

```python
# 使用縮圖模式（預設，減少 token 消耗）
get_attachment_image(attachment_id=123)

# 指定縮圖最大尺寸
get_attachment_image(attachment_id=123, max_size=600)

# 取得原始大小圖片（不縮圖）
get_attachment_image(attachment_id=123, thumbnail=False)
```

### 使用流程範例
```
1. get_issue(123) → 取得議題，查看附件列表
2. get_attachment_info(456) → 確認附件資訊
3. get_attachment_image(456) → AI 視覺分析圖片內容
```

### 功能特色
- **縮圖模式**: 預設啟用，將大圖縮小至 800px，大幅減少 token 消耗
- **格式轉換**: 自動轉換為 JPEG 格式，優化檔案大小
- **透明度處理**: PNG 透明背景自動轉為白色
- **錯誤處理**: 非圖片類型、檔案過大等情況會返回友好訊息

### 支援的圖片格式
- PNG (`image/png`)
- JPEG (`image/jpeg`)
- GIF (`image/gif`)
- WebP (`image/webp`)

### 限制
- 檔案大小上限：10 MB
- 預設縮圖尺寸：800 px（最大邊長）

## 時間記錄功能 ✨

### add_issue_note 時間記錄支援
現在可以在新增議題備註時同時記錄工作時間：

```python
# 新增備註並記錄時間（使用活動名稱）
add_issue_note(
    issue_id=1,
    notes="完成功能開發",
    spent_hours=2.5,
    activity_name="開發"
)

# 新增備註並記錄時間（使用活動 ID）
add_issue_note(
    issue_id=1,
    notes="修復 bug",
    spent_hours=1.0,
    activity_id=12,
    spent_on="2025-06-25"  # 指定記錄日期
)

# 私有備註 + 時間記錄
add_issue_note(
    issue_id=1,
    notes="內部討論記錄",
    private=True,
    spent_hours=0.5,
    activity_name="討論"
)

# 僅新增備註（向後相容）
add_issue_note(issue_id=1, notes="一般備註")
```

### 時間追蹤活動支援
系統支援以下預設活動：
- 設計 (ID: 10)
- 開發 (ID: 11)
- 除錯 (ID: 12)
- 調查 (ID: 13)
- 討論 (ID: 14)
- 測試 (ID: 15)
- 維護 (ID: 16)
- 文件 (ID: 17)
- 教學 (ID: 18)
- 翻譯 (ID: 19)
- 其他 (ID: 20)

### 特色功能
- **智慧快取**: 時間追蹤活動資訊自動快取，提升查詢效率
- **名稱參數**: 支援使用活動名稱而非 ID，使用更直觀
- **向後相容**: 保持原有 `add_issue_note` 功能完全相容
- **錯誤提示**: 無效活動名稱時自動顯示可用選項
- **彈性日期**: 可指定記錄日期，預設為今日

## 注意事項

- 專案正在開發初期階段
- 後續會根據開發進度更新此檔案內容