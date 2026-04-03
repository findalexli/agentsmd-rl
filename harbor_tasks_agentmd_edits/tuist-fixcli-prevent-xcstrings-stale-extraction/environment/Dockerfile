FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone tuist at base commit
RUN git init /workspace/tuist && \
    cd /workspace/tuist && \
    git remote add origin https://github.com/tuist/tuist.git && \
    git fetch --depth=1 origin 48207131f1e248413d59a0dab0044fd3c2dbb48a && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/tuist

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
