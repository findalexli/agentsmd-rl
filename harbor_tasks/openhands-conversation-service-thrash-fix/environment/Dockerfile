FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (needed for some OpenHands build steps)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry uv

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=024f4d3326363616f2303e1fafb93224c8bb7ddb
RUN git clone --filter=blob:none --single-branch --depth=100 https://github.com/All-Hands-AI/OpenHands.git openhands \
    && cd openhands \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/openhands

# Install Python dependencies using poetry
# First, install only production dependencies (no dev dependencies to save time)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without test,dev --no-root || true

# Also install via pip as fallback for any missing deps
RUN pip install fastapi pydantic pytest pytest-asyncio httpx uvicorn || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Keep container running
CMD ["tail", "-f", "/dev/null"]

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages pre-commit 2>/dev/null || pip install --no-cache-dir pre-commit
