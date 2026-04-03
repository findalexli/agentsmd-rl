FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone PyTorch at the base commit (before the fix)
RUN git init /workspace/pytorch && \
    cd /workspace/pytorch && \
    git remote add origin https://github.com/pytorch/pytorch.git && \
    git fetch --depth=1 origin 4b8a514606230b60bb8f27be5f11612f21b4aec1 && \
    git checkout FETCH_HEAD

# Configure git
RUN cd /workspace/pytorch && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pytorch