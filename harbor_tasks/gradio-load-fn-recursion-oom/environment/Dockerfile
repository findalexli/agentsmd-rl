FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the buggy commit (parent of fix PR #12928)
RUN git init /repo \
    && cd /repo \
    && git remote add origin https://github.com/gradio-app/gradio.git \
    && git fetch --depth=1 origin ca84f3e36c6a3f3c3f0b57084b6f514d6cded1d4 \
    && git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install gradio backend (needed for behavioral tests)
RUN pip install --no-cache-dir -e . 2>&1 | tail -3 || true

# Install ruff for formatting checks
RUN pip install --no-cache-dir ruff

RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

ENV PYTHONPATH=/repo