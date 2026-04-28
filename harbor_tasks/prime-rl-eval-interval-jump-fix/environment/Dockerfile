FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Pinned test deps. We deliberately do NOT install prime-rl's runtime deps
# (torch, vllm, flash-attn, etc.). The targeted function under test is pure
# Python; tests load eval_utils.py via importlib with the heavy module
# imports stubbed out, so the runtime stack is not needed.
# ruff is needed for the CI-derived lint check that validates the changed
# orchestrator files remain lint-clean (the repo's Style CI job does this).
RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        ruff==0.13.0

WORKDIR /workspace

RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin f655f71c33e75dc9d78adefc13f0809d2002485c && \
    git checkout FETCH_HEAD

WORKDIR /workspace/prime-rl

RUN mkdir -p /logs/verifier
