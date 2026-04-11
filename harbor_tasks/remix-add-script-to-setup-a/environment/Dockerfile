FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Remix monorepo — shallow clone at base commit
RUN git init /workspace/remix && \
    cd /workspace/remix && \
    git remote add origin https://github.com/remix-run/remix.git && \
    git fetch --depth=1 origin 598a92e3dc3488b02da7e4edafd1ff2498cc4c34 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
