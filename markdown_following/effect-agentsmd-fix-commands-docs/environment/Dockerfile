FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/effect-ts/effect.git && \
    git fetch --depth=1 origin 5487cfb65a69a308e7c0b29ae666c8a9ddcab159 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/effect

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
