FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# openai-agents-js — use shallow snapshot
RUN git init /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git remote add origin https://github.com/openai/openai-agents-js.git && \
    git fetch --depth=1 origin 4e6b3fbd3355709831a1bb64472b3c947b694690 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/openai-agents-js

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
