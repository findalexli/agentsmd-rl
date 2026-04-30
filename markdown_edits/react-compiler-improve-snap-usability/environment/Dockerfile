FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone — tests only read source files, no build needed
RUN git init /workspace/react && \
    cd /workspace/react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin 24d8716e366909129ffd66670e1e530e6796097d && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
