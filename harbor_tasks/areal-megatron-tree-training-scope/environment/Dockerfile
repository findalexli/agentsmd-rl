FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/inclusionAI/AReaL.git /workspace/AReaL && \
    cd /workspace/AReaL && \
    git checkout 933218365af85d5488a554367d9fbe5071442b49 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/AReaL

# No heavy deps needed — tests do AST/source analysis only
# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
