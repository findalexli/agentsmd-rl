FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone transformers at the base commit (BEFORE the fix)
ARG BASE_COMMIT=6a056a16a856097cb0400ce9a48e96ab9d469e30
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout ${BASE_COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Configure git for the agent
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent" && \
    git config --global --add safe.directory /workspace/transformers

# Install minimal deps needed for testing (no torch/GPU)
# Base transformers only — [dev] pulls torch/tf/datasets and causes build timeout
RUN pip install --no-cache-dir jinja2 tokenizers && \
    pip install --no-cache-dir -e .

ENV PYTHONPATH="/workspace/transformers/src:${PYTHONPATH}"

# Copy test and solution files