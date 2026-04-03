FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone gradio at the base commit (before the fix)
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin d610464e0eff5f200543c6bbc5fac616b1620b1e && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio

# Install minimal Python deps needed for testing (no heavy ML deps)
RUN pip install --no-cache-dir \
    ruff \
    pyyaml \
    && pip install --no-cache-dir -e . 2>/dev/null || \
    pip install --no-cache-dir -e ".[dev]" 2>/dev/null || \
    echo "Install attempted"

ENV PYTHONPATH=/workspace/gradio