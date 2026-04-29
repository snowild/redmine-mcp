# Redmine MCP Server Dockerfile
# Multi-stage build to reduce final image size

# ===== Build stage =====
FROM python:3.12-slim AS builder

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Use uv to install dependencies into virtual environment
RUN uv sync --frozen --no-dev

# ===== Runtime stage =====
FROM python:3.12-slim AS runtime

# Install curl (for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp

# Set working directory
WORKDIR /app

# Copy virtual environment and source code from build stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Default SSE configuration
ENV REDMINE_MCP_TRANSPORT=sse
ENV REDMINE_MCP_HOST=0.0.0.0
ENV REDMINE_MCP_PORT=8000

# Create config directory for user profiles
RUN mkdir -p /home/mcp/.redmine_mcp && chown -R mcp:mcp /home/mcp/.redmine_mcp

# Switch to non-root user
USER mcp

# Expose default SSE port
EXPOSE 8000

# Health check (check if SSE endpoint responds)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -sf http://localhost:8000/sse --max-time 5 > /dev/null || exit 1

# Start service
CMD ["python", "-m", "redmine_mcp.server", "--transport", "sse"]
