FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Angular monorepo — use shallow clone with sparse checkout for speed
RUN git clone --filter=blob:none https://github.com/angular/angular.git /workspace/angular && \
    cd /workspace/angular && \
    git checkout c1261b02dbe1d995d5a6fccb5556aca4d67b529f && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/angular

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
