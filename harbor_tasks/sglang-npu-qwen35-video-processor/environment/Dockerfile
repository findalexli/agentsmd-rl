FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout 931dbceadc49eb36d6f76477e5666a03c7c641ca && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Install torch for tests (CPU-only is fine for testing the logic)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install transformers (needed by the module under test)
RUN pip install --no-cache-dir transformers

# Install additional dependencies needed by sglang
RUN pip install --no-cache-dir pybase64 numpy pydantic

# Verifier output directory
RUN mkdir -p /logs/verifier
