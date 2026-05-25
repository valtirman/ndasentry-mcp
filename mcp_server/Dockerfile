# syntax=docker/dockerfile:1.6
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps for HTTPS to ndasentry.ai backend
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install python deps first (cached layer)
COPY mcp_server/requirements.txt ./
RUN pip install -r requirements.txt

# Copy MCP server source
COPY mcp_server/ ./mcp_server/

# Railway provides $PORT; default to 1966 for local docker testing
ENV PORT=1966
EXPOSE 1966

# Boot
CMD python -m mcp_server.server
