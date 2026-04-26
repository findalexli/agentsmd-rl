FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin bbaa7698227fcf4f7ec001af6aa5110d405ee54f && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/ruff

# Install mypy-primer from git (needed by the new script's imports at test time)
RUN pip install --no-cache-dir git+https://github.com/hauntsaninja/mypy_primer.git

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages typos validate-pyproject 2>/dev/null || pip install --no-cache-dir typos validate-pyproject
