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
    git fetch --depth=1 origin f161c261ef8fd77ff327a4e41104317ad00b7b08 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sim

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
