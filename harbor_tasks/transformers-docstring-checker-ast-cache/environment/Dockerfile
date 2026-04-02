FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone transformers at the base commit (before the fix)
ARG BASE_COMMIT=1f553bdc1703c78e272656ab8fb86d6494593e18
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout ${BASE_COMMIT}

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir ruff pytest-json-ctrf

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Install transformers in editable mode (needed for check_docstrings imports)
# plus quality tools for ruff
RUN pip install --no-cache-dir -e ".[quality]" 2>&1 | tail -5

# Configure git user for any git operations
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH="/workspace/transformers/utils:/workspace/transformers/src:${PYTHONPATH}"