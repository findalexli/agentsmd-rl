FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone sglang repo at base commit
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin bb9e058f5b9d4754ac2965bb36864fee1cd978e8 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Install minimal deps needed for test analysis
RUN pip install --no-cache-dir requests

# Verifier output directory
RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages pre-commit 2>/dev/null || pip install --no-cache-dir pre-commit
