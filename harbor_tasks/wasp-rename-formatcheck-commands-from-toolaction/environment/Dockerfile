FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/wasp && \
    cd /workspace/wasp && \
    git remote add origin https://github.com/wasp-lang/wasp.git && \
    git fetch --depth=1 origin 0ea59a851ef61e08184adc018e9b20801243ed8d && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/wasp

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
