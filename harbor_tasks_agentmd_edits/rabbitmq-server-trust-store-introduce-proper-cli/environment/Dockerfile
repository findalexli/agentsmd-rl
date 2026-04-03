FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# rabbitmq-server is a large monorepo — use shallow clone
RUN git init /workspace/rabbitmq-server && \
    cd /workspace/rabbitmq-server && \
    git remote add origin https://github.com/rabbitmq/rabbitmq-server.git && \
    git fetch --depth=1 origin 95cfcbac9099290f72f99665a8b9ba7f63a8c266 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/rabbitmq-server

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
