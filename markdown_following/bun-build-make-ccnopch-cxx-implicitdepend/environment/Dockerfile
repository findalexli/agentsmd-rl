FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit (bun is a huge monorepo)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 485ec522a22b469b336aece8276b507a71665a87 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/bun

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
