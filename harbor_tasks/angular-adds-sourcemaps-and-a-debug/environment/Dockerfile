FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# angular/angular is large — use shallow snapshot approach
RUN git init /workspace/angular && \
    cd /workspace/angular && \
    git remote add origin https://github.com/angular/angular.git && \
    git fetch --depth=1 origin f30ed6bbf6706790437a6e4dbfffed3fa8708f57 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/angular

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
