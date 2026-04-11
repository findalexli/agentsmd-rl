FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo, use blob filter)
RUN git clone --filter=blob:none https://github.com/angular/angular.git /workspace/angular && \
    cd /workspace/angular && \
    git checkout d75046bc091699bbadcb5f2032be627e983ee6fa && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/angular

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
