FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin c2b99e69ce31c71261f56c97fbd2ed467258f940 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl

# Configure git for the agent
RUN git config --global user.email "agent@example.com" \
    && git config --global user.name "Agent"

# Install minimal deps for testing (no torch/vllm - tests use mocks)
RUN pip install --no-cache-dir pytest pytest-json-ctrf

ENV PYTHONPATH=/workspace/prime-rl/src