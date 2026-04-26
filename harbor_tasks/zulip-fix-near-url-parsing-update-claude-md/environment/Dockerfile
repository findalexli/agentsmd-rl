FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/zulip && \
    cd /workspace/zulip && \
    git remote add origin https://github.com/zulip/zulip.git && \
    git fetch --depth=1 origin 305c52c35a7dad3e6c9bde470e8f717186abaae5 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/zulip

# Install deps needed by test_outputs.py (orjson/requests for importing the fetch script)
RUN pip install --no-cache-dir orjson requests

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
