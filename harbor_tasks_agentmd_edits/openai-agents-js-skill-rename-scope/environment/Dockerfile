FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git checkout 41c1b89f650a9d18aeb76677f965dcfb06087c90 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/openai-agents-js

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
