FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit (grafana/mimir is a large monorepo)
RUN git init /workspace/mimir && \
    cd /workspace/mimir && \
    git remote add origin https://github.com/grafana/mimir.git && \
    git fetch --depth=1 origin 1ab789daf1b3d9393386b302622d2906bc08b2dc && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mimir

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
