FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit
RUN git init /workspace/react && \
    cd /workspace/react && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin b354bbd2d231fdeeec31d438c8e7c54877eee4ac && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
