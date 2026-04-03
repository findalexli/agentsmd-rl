FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone expo monorepo at base commit (shallow)
RUN git init /workspace/expo && \
    cd /workspace/expo && \
    git remote add origin https://github.com/expo/expo.git && \
    git fetch --depth=1 origin a6d7308929a768de78b5c39b79f71572e6865bca && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/expo

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
