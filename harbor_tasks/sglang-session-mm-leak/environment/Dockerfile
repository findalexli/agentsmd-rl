FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ARG REPO_COMMIT=c2b3e42ad64521c018443f7efe294658a0b1da3b
RUN git clone --depth=1 --filter=blob:none https://github.com/sgl-project/sglang.git /workspace && \
    cd /workspace && \
    git checkout ${REPO_COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /workspace

ENV PYTHONPATH="/workspace/python:${PYTHONPATH}"

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages black codespell isort ruff 2>/dev/null || pip install --no-cache-dir black codespell isort ruff
