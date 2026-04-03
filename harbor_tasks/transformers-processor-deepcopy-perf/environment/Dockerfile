FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone transformers at the base commit (BEFORE the fix)
ARG BASE_COMMIT=55cc1a7fb8e53a5e7e35ca9cf9759498f20abb93
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Configure git for the agent
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent" && \
    git config --global --add safe.directory /workspace/transformers

# Install tokenizers binary wheel first (avoids Rust build requirement)
RUN pip install --no-cache-dir tokenizers

# Install minimal deps needed for testing (no torch/GPU)
RUN pip install --no-cache-dir -e ".[dev]" jinja2 || pip install --no-cache-dir -e . jinja2 tokenizers
RUN pip install --no-cache-dir ruff

ENV PYTHONPATH="/workspace/transformers/src:${PYTHONPATH}"

# Copy test and solution files