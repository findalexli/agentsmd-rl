FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin 7160b6cb76d3619468b219ea066fcb6358a8000e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

# Install minimal deps for testing (no torch/GPU — we only need stdlib + ast parsing)
# The fsdp_load.py file imports torch but our tests extract and test the pure-python
# helper function directly, so we don't need torch installed.
RUN pip install --no-cache-dir pyyaml

# Configure git for any commits the agent may make
RUN git config user.email "agent@test.com" && git config user.name "Agent"

ENV PYTHONPATH=/workspace/sglang/python

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages black codespell isort pre-commit ruff 2>/dev/null || pip install --no-cache-dir black codespell isort pre-commit ruff
