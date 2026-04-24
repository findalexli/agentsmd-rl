FROM python:3.12-slim

WORKDIR /workspace

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone OpenHands repo at base commit
ARG BASE_COMMIT=d6a0dd7fe4a7002e77947a23a61656b9dab6eceb
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git /workspace/OpenHands && \
    cd /workspace/OpenHands && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/OpenHands

# Install Python dependencies (minimal for testing)
RUN pip install pytest pytest-asyncio httpx jinja2

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set Python path to include the repo
ENV PYTHONPATH=/workspace/OpenHands:$PYTHONPATH

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
