FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/electric && \
    cd /workspace/electric && \
    git remote add origin https://github.com/electric-sql/electric.git && \
    git fetch --depth=1 origin 551cb0265c7d4b53b8cba6d9fc8181997c463940 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/electric

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
