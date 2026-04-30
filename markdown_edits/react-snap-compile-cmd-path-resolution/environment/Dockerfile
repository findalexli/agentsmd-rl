FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

# Shallow clone React at base commit — large monorepo, only need compiler/
RUN git init /workspace/react && \
    cd /workspace/react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin cd0c4879a2959db91f9bd51a09dafefedd95fb17 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react
