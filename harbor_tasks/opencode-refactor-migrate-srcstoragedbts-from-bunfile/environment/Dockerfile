FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before PR #14124)
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout 57b63ea83d5926ee23f72185c6fb8894654e2981 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
