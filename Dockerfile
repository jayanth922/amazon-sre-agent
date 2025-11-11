# Use uv's ARM64 Python base image
FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy uv files
COPY pyproject.toml uv.lock ./

# Install dependencies (must include FastAPI, Uvicorn, etc. for ALL services)
RUN uv sync --frozen --no-dev

# Copy source code (entire repo so both sre_agent and gateway modules exist)
COPY . .

# Set environment variables
ENV PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose port (informational; compose handles binding)
EXPOSE 8080

# Default CMD (overridden per-service in compose)
CMD ["uv", "run", "opentelemetry-instrument", "uvicorn", "sre_agent.agent_runtime:app", "--host", "0.0.0.0", "--port", "8080"]
