FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git checkout b54fc4a3222ea8b14b1c3a8e45457b4905354bee && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/openai-agents-js

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
