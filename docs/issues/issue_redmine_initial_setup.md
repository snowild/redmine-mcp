# Issue: Redmine 初始設定需求補充

## 問題描述

用戶反映即使啟用了 REST API 並取得 API 金鑰，仍然無法正常建立議題。這是因為 Redmine 需要完整的基本資料設定才能正常運作。

## 發現

Redmine 系統在開始使用前需要設定：
1. **角色與權限** - 定義用戶可以執行的操作
2. **追蹤器** - 定義議題類型（如：缺陷、功能、支援）
3. **議題狀態** - 定義議題的生命週期狀態
4. **工作流程** - 定義狀態之間的轉換規則
5. **專案設定** - 建立專案並指派成員

## 影響

- 沒有這些設定，`create_new_issue` 會失敗
- `update_issue_status` 可能因工作流程限制而失敗
- `close_issue` 需要至少一個「已關閉」狀態
- 權限不足會導致所有操作失敗

## 解決方案

### 1. 更新文件
- ✅ 在 README.md 中新增「4.2 設定 Redmine 基本資料」章節
- ✅ 擴展故障排除部分，包含設定相關問題
- ✅ 建立詳細的設定指南 `docs/manuals/redmine_setup_guide.md`

### 2. 建立設定指南
建立完整的設定指南包含：
- 角色與權限設定
- 追蹤器設定
- 議題狀態設定
- 工作流程設定
- 專案建立
- 驗證步驟
- 常見問題解決

### 3. 設定檢查清單
提供一個可檢查的設定項目清單，確保用戶不會遺漏任何重要步驟。

## 建議改進

### 短期
- ✅ 更新現有文件
- ✅ 建立詳細設定指南

### 中期
- 考慮建立設定驗證工具，檢查 Redmine 基本設定是否完整
- 在 MCP 工具中加入更友善的錯誤訊息，提示缺少的設定

### 長期
- 考慮建立自動化設定腳本，協助用戶快速完成基本設定
- 整合設定檢查到 `health_check` 工具中

## 相關檔案

- `/README.md` - 主要文件，包含基本設定步驟
- `/docs/manuals/redmine_setup_guide.md` - 詳細設定指南
- `/docs/issues/issue_redmine_initial_setup.md` - 此問題記錄

## 狀態

✅ **已解決** - 文件已更新，包含完整的 Redmine 設定指南

## 測試

用戶應該能夠：
1. 按照 README.md 的步驟完成基本設定
2. 參考詳細設定指南完成完整設定
3. 使用設定檢查清單驗證設定完整性
4. 成功建立和管理議題

## 經驗教訓

- Redmine 是一個功能豐富但設定複雜的系統
- 使用者文件需要考慮不同經驗層級的用戶
- 提供多層次的文件（快速設定 + 詳細指南）是必要的
- 設定驗證和檢查清單能大幅降低用戶困惑