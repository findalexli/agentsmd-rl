FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone — large monorepo)
RUN git clone --filter=blob:none https://github.com/triggerdotdev/trigger.dev.git /workspace/trigger.dev && \
    cd /workspace/trigger.dev && \
    git checkout 688b108ec3283fc738a416a6a44ab4abb0ab1fd5 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/trigger.dev

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
