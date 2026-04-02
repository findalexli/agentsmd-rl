FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
ARG REPO_URL=https://github.com/inclusionAI/AReaL.git
ARG BASE_COMMIT=682d5640a3497dd69e6ea2b98d2a0f45f34df578

RUN git clone "$REPO_URL" /repo && \
    cd /repo && \
    git checkout "$BASE_COMMIT"

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps for testing (CPU-only torch for imports)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir colorlog

# Configure git for potential patch application
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH=/repo