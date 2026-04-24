FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Install torch CPU-only (needed for behavioral tests)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Clone repo at base commit (before fix)
ARG BASE_COMMIT=677424c7acd9fb7477294017c99f798588002d4f
RUN git init /workspace/vllm && \
    cd /workspace/vllm && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

# Configure git for agent use
RUN cd /workspace/vllm && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

ENV PYTHONPATH="/workspace/vllm"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vllm

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages mypy ruff typos 2>/dev/null || pip install --no-cache-dir mypy ruff typos
