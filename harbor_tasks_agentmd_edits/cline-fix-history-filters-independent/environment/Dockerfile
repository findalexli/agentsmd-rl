FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/cline/cline.git /workspace/cline && \
    cd /workspace/cline && \
    git checkout 9fc9785aa2ab3985ae5030330566499d26fb6192 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/cline

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
