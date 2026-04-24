FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
ARG REPO_URL=https://github.com/inclusionAI/AReaL.git
ARG BASE_COMMIT=61281ba8851e6d1cf8c30794a5391359b4e324b7

RUN git clone --depth=1 --filter=blob:none "$REPO_URL" /repo && \
    cd /repo && \
    git checkout "$BASE_COMMIT"

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps for testing (CPU-only torch for type annotations / AST)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir transformers peft

# Configure git for potential patch application
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH=/repo

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
