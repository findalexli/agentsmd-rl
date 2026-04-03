FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=6208006db64ac29aded7be33963e86503ba9e28e

RUN git init /workspace/AReaL && \
    cd /workspace/AReaL && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL

# Install minimal deps needed for testing (no torch/GPU packages)
# We only need the source tree; tests use AST parsing and direct imports of small modules
RUN pip install --no-cache-dir pyyaml

# Configure git for any agent that wants to commit
RUN git config --global user.email "agent@test.local" && \
    git config --global user.name "Test Agent"

ENV PYTHONPATH="/workspace/AReaL:${PYTHONPATH:-}"