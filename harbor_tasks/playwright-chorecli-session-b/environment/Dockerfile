FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 605d93d732c5ab752ae314ac47fdd6ad3abc11de && \
    git checkout 605d93d732c5ab752ae314ac47fdd6ad3abc11de && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install npm dependencies for the repo
RUN npm ci

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
