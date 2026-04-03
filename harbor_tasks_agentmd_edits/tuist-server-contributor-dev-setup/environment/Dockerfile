FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow fetch for large monorepo)
RUN git init /workspace/tuist && \
    cd /workspace/tuist && \
    git remote add origin https://github.com/tuist/tuist.git && \
    git fetch --depth=1 origin 37e098781f47d8ba89bf9afe88817671dddecfc2 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/tuist

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
