FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone for large repo)
RUN git clone --filter=blob:none https://github.com/zulip/zulip.git /workspace/zulip && \
    cd /workspace/zulip && \
    git checkout 305c52c35a7dad3e6c9bde470e8f717186abaae5 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/zulip

# Install deps needed by test_outputs.py (for importing the URL parser module)
RUN pip install --no-cache-dir orjson requests

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
