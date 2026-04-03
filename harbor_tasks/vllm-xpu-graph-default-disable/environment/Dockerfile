FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin a9213c0ffea4c6485dd1d03de5e8b3ff96dda924 && \
    git checkout FETCH_HEAD

# Configure git for the agent
RUN cd /repo && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

ENV PYTHONPATH=/repo
RUN mkdir -p /logs/verifier

WORKDIR /repo