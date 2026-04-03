FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# tuist/tuist is a large monorepo — use shallow clone
RUN git init /workspace/tuist && \
    cd /workspace/tuist && \
    git remote add origin https://github.com/tuist/tuist.git && \
    git fetch --depth=1 origin 10f2ade970563161cd32699f45d87c8b891417e0 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/tuist

# No additional deps needed — tests are file-content checks (Elixir repo)
# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
