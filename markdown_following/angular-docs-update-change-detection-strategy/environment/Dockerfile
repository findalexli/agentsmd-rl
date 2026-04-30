FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Angular monorepo — use shallow clone with sparse checkout for speed
RUN git init /workspace/angular && \
    cd /workspace/angular && \
    git remote add origin https://github.com/angular/angular.git && \
    git fetch --depth=1 origin c1261b02dbe1d995d5a6fccb5556aca4d67b529f && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/angular

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
