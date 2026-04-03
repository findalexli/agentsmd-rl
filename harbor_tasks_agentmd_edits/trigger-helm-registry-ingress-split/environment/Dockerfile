FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — shallow clone)
RUN git clone --depth=1 https://github.com/triggerdotdev/trigger.dev.git /workspace/trigger.dev && \
    cd /workspace/trigger.dev && \
    git fetch --depth=50 origin dc568e7f3edc168defc0a7e9afab382eba770bf1 && \
    git checkout dc568e7f3edc168defc0a7e9afab382eba770bf1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/trigger.dev

# Install deps needed by test_outputs.py (YAML parsing)
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
