FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone — tests only read file content
RUN git init /workspace/sim && \
    cd /workspace/sim && \
    git remote add origin https://github.com/simstudioai/sim.git && \
    git fetch --depth=1 origin 8f3e8647512febc6156b66e8f6ea1961e15f589a && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sim

# Install test deps (pyyaml for YAML parsing checks)
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
