FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none --single-branch https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout 23b2d8514f13f109b980b0a1f4f3aab906ad51d0 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
