FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Install test dependencies (numpy + pandas for eval_utils metrics)
RUN pip install --no-cache-dir numpy pandas pyyaml

# Clone repo at base commit (BEFORE the fix) — shallow fetch for speed
RUN git init /workspace \
    && cd /workspace \
    && git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git \
    && git fetch --depth 1 origin 60f01a04681df563044cf3cb7c64ec480b608451 \
    && git checkout FETCH_HEAD \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

ENV PYTHONPATH="/workspace/src:${PYTHONPATH}"
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
