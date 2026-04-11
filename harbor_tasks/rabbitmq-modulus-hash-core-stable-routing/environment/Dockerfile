FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow snapshot for large monorepo)
RUN git init /workspace/rabbitmq-server && \
    cd /workspace/rabbitmq-server && \
    git remote add origin https://github.com/rabbitmq/rabbitmq-server.git && \
    git fetch --depth=1 origin 713ecee4846a2816cf828e877820f0f509674f67 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/rabbitmq-server

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
