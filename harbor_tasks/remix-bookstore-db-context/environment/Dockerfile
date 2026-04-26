FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# python3 needed by pytest test runner
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use blob filter)
RUN git init /workspace/remix && \
    cd /workspace/remix && \
    git remote add origin https://github.com/remix-run/remix.git && \
    git fetch --depth=1 origin b29fc874293468babb25b90e95edc208f1d652be && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
