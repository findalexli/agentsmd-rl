FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (BEFORE the fix)
RUN git init /workspace/vllm && \
    cd /workspace/vllm && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin 03ac6ca8954d491dc39ae169c2623e8ccffba7c6 && \
    git checkout FETCH_HEAD

# Configure git user for the agent
RUN cd /workspace/vllm && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

ENV PYTHONPATH=/workspace/vllm
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vllm