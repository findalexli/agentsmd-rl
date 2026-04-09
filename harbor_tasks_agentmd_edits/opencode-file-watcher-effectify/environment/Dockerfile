FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin d4694d058cc590b0f05261a04460034d2fa8541d && \
    git checkout FETCH_HEAD

WORKDIR /workspace/opencode

RUN git config user.email "agent@test" && git config user.name "Agent"

RUN mkdir -p /logs/verifier
