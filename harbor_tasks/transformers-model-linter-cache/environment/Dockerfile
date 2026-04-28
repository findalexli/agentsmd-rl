FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux make && \
    rm -rf /var/lib/apt/lists/*

# Clone transformers at the base commit (before the fix)
ARG BASE_COMMIT=aa1c36f1a9f454e69c4eac83071ced235942c7ed
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Install minimal deps: rich (for Console), ruff (for config-derived checks)
RUN pip install --no-cache-dir rich ruff pytest pytest-json-ctrf

# Configure git user for any git operations
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH="/workspace/transformers/utils:/workspace/transformers/src"