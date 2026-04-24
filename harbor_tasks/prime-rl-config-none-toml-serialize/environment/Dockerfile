FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at base commit (before the fix)
RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin 692dfc8a4b9471e65004d8ac154d07ebb73bc61c && \
    git checkout FETCH_HEAD

# Install only what tests need
RUN pip install --no-cache-dir tomli_w pytest pytest-json-ctrf

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir pydantic pydantic-settings
RUN pip install --no-cache-dir "pydantic-config @ git+https://github.com/samsja/pydantic_config.git@main"

ENV PYTHONPATH="/workspace/prime-rl/src:${PYTHONPATH:-}"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
