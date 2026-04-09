FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/oxc-project/oxc.git /workspace/oxc && \
    cd /workspace/oxc && \
    git checkout 828b56a30708f7db749405f245262ca53125fc1b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/oxc

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
