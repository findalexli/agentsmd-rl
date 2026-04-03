FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for speed — large monorepo)
RUN git init /workspace/mantine && \
    cd /workspace/mantine && \
    git remote add origin https://github.com/mantinedev/mantine.git && \
    git fetch --depth=1 origin 2281c3859b4f26227d2f1f371aaa9258d3a8dbd8 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mantine

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
