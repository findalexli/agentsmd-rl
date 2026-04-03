FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# payloadcms/payload is large — use shallow snapshot approach
RUN git init /workspace/payload && \
    cd /workspace/payload && \
    git remote add origin https://github.com/payloadcms/payload.git && \
    git fetch --depth=1 origin 7f3c6c8f4628fb066002e2fd5c3cc6b83ddf4ccc && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
