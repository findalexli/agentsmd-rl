FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Backstage is a huge monorepo — use shallow clone with single branch
RUN git init /workspace/backstage && \
    cd /workspace/backstage && \
    git remote add origin https://github.com/backstage/backstage.git && \
    git fetch --depth=1 origin 7c99d4f3021c375b4dea1bae6156ccbf527580e3 && \
    git checkout 7c99d4f3021c375b4dea1bae6156ccbf527580e3 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/backstage

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
