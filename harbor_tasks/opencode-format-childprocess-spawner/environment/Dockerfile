FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before PR #19457)
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout c8909908f50afc3622d354cd8fd7a83dc3445706 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
