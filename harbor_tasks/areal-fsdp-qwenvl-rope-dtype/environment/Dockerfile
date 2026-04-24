FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin f6556e88582e82b747ab1ac4038af2e106a464ee && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps for testing (no torch/GPU — tests use AST + mock)
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Copy test harness

ENV PYTHONPATH="/repo"

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages pre-commit ruff 2>/dev/null || pip install --no-cache-dir pre-commit ruff
