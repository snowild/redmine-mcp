# Redmine MCP Server Dockerfile
# 多階段建置以減少最終映像大小

# ===== 建置階段 =====
FROM python:3.12-slim AS builder

# 安裝 uv 套件管理器
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 設定工作目錄
WORKDIR /app

# 複製專案檔案
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# 使用 uv 安裝依賴到虛擬環境
RUN uv sync --frozen --no-dev

# ===== 執行階段 =====
FROM python:3.12-slim AS runtime

# 安裝 curl（用於健康檢查）
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 建立非 root 用戶
RUN useradd --create-home --shell /bin/bash mcp

# 設定工作目錄
WORKDIR /app

# 從建置階段複製虛擬環境和原始碼
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# 設定環境變數
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# 預設 SSE 配置
ENV REDMINE_MCP_TRANSPORT=sse
ENV REDMINE_MCP_HOST=0.0.0.0
ENV REDMINE_MCP_PORT=8000

# 切換到非 root 用戶
USER mcp

# 暴露 SSE 預設埠
EXPOSE 8000

# 健康檢查（檢查 SSE endpoint 是否回應）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -sf http://localhost:8000/sse --max-time 5 > /dev/null || exit 1

# 啟動服務
CMD ["python", "-m", "redmine_mcp.server", "--transport", "sse"]
