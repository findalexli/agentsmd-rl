FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large Rust monorepo — use blob filter)
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git /workspace/uv && \
    cd /workspace/uv && \
    git checkout dd0d76cd83821e22a7054de21eb73051eb23274d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/uv

# Install deps needed by test_outputs.py
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
