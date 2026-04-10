FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip python3-venv tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit — large monorepo
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 982b9b279557229b12d049ebd3063da408ba5253 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install npm dependencies for the monorepo
RUN npm ci

# Build the monorepo to generate required files (tsc and check-deps need this)
RUN npm run build

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
