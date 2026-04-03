FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone electron at base commit (huge repo — depth=1 only)
RUN git init /workspace/electron && \
    cd /workspace/electron && \
    git remote add origin https://github.com/electron/electron.git && \
    git fetch --depth=1 origin 378659c535b2b0a92bdbe82a790fa0799e53df9f && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/electron

# Tests only check markdown file contents — no project deps needed
RUN pip install --no-cache-dir pytest pytest-json-ctrf pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
