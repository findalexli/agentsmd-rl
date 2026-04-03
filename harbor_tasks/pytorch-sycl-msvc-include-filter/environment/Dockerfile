FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone pytorch at the base commit (before the fix)
RUN git init /workspace/pytorch && \
    cd /workspace/pytorch && \
    git remote add origin https://github.com/pytorch/pytorch.git && \
    git fetch --depth=1 origin dc12b65cd31ba18cbdc7f2e12e7d1564a67770d0 && \
    git checkout FETCH_HEAD

# Configure git user for agent commits
RUN cd /workspace/pytorch && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

# No torch install needed — tests operate on the source file directly
RUN pip install --no-cache-dir pytest pytest-json-ctrf

ENV PYTHONPATH="/workspace/pytorch"
RUN mkdir -p /logs/verifier

WORKDIR /workspace/pytorch