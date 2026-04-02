FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
ARG REPO_URL=https://github.com/inclusionAI/AReaL.git
ARG BASE_COMMIT=cbe35f5a4b866596d996d5690085eda0577708f5

RUN git clone "$REPO_URL" /repo && \
    cd /repo && \
    git checkout "$BASE_COMMIT"

RUN pip install --no-cache-dir httpx

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps for testing (no torch/GPU — just need the source for AST/grep checks)
# The platform module needs torch for type annotations, so install CPU-only torch
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir transformers

# Configure git for potential patch application
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH=/repo