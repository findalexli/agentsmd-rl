FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow — large monorepo)
RUN git init /workspace/payload && \
    cd /workspace/payload && \
    git remote add origin https://github.com/payloadcms/payload.git && \
    git fetch --depth=1 origin 5efc2ffa032b6b5f908b9c94c34276f23a62b71d && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# No project deps needed — tests only read/parse files
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
