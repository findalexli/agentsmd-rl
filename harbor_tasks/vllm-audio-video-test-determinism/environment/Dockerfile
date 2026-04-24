FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (BEFORE the fix)
RUN git init /workspace/vllm && \
    cd /workspace/vllm && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin c133f3374625652c88e122fff995e4126c4635c0 && \
    git checkout FETCH_HEAD

# Configure git user for the agent
RUN cd /workspace/vllm && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

ENV PYTHONPATH=/workspace/vllm
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vllm

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
