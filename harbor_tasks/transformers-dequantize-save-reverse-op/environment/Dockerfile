FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
ARG BASE_COMMIT=12b6b57cac0397db0afda56f3ab0101729bc5f0f
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install transformers from source with minimal deps + torch CPU for testing
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -e "." && \
    pip install --no-cache-dir ruff pyyaml pytest pytest-json-ctrf

# Configure git for potential commits
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH=/repo/src