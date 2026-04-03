FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone transformers at the base commit (before the fix)
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 20a233bdc5c0fae8fa116184f105adf498d44ba2 && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Install ruff for style checks (config-derived grading)
RUN pip install --no-cache-dir ruff

# Configure git user for applying patches
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

ENV PYTHONPATH="/workspace/transformers/src:${PYTHONPATH:-}"