FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

# Clone sglang at the commit BEFORE the fix
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin c06ca1526cb6008a8dacb4fdb06567e648134664 && \
    git checkout FETCH_HEAD

# Install minimal deps for the modules to be parseable/importable
RUN pip install --no-cache-dir psutil numpy && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || true

ENV PYTHONPATH="/workspace/sglang/python"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/sglang

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages black codespell isort ruff 2>/dev/null || pip install --no-cache-dir black codespell isort ruff
