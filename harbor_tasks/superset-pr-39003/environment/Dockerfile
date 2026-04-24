# Dockerfile for superset-mcp-execute-sql-limit-suggestion task
FROM python:3.12-slim

# Install git and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git && \
    cd superset && \
    git checkout c5bce756f0c3918620babd88d87b4cdadf3f711a

WORKDIR /workspace/superset

# Install only the dependencies needed for the MCP service utils (minimal)
RUN pip install --no-cache-dir pydantic tiktoken

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
