FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/wasp-lang/wasp.git /workspace/wasp && \
    cd /workspace/wasp && \
    git checkout a9d31fbab364485fcd01d9edf1c729d1cc78e564 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/wasp

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
