FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit, also fetch merge commit for gold apply
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 25d303f03424011dc0ad36d027a7af3368618eab && \
    git checkout FETCH_HEAD && \
    git fetch --depth=1 origin e0e7f41e80247f857e97cb23f4833d2eee2122fe && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
