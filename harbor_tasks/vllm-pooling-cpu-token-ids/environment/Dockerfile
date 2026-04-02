FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (BEFORE the fix)
RUN git clone https://github.com/vllm-project/vllm.git /workspace/vllm && \
    cd /workspace/vllm && \
    git checkout 8c0b6267d7fa5c8a07e318809180fc021a0afbf2

# Install torch CPU-only for behavioral testing
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Configure git user for the agent
RUN cd /workspace/vllm && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

ENV PYTHONPATH=/workspace/vllm
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vllm