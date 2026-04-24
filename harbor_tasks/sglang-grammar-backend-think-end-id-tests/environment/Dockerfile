FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin 5dd2c243eb52dfd04f27b998e2595fe0c66437b1 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

# No heavy deps needed — tests use AST analysis and text-based verification,
# not runtime imports (sglang imports torch at top-level)
ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH}"

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages black codespell isort ruff 2>/dev/null || pip install --no-cache-dir black codespell isort ruff
