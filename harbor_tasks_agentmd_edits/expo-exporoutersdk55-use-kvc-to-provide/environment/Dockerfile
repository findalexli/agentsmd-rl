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
    git fetch --depth=1 origin c6a0b6755b9dbb60900cb226926afe21f98acd6c && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/expo

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
