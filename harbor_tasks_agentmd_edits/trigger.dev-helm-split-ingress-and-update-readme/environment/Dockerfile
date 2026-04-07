FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — blob filter)
RUN git clone --filter=blob:none https://github.com/triggerdotdev/trigger.dev.git /workspace/trigger.dev && \
    cd /workspace/trigger.dev && \
    git checkout dc568e7f3edc168defc0a7e9afab382eba770bf1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/trigger.dev

# Install deps for test_outputs.py (YAML parsing)
RUN pip install --no-cache-dir pyyaml

# Verifier output directory
RUN mkdir -p /logs/verifier
