FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git python3 python3-pip python3-venv build-essential ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout f944b4c5352be02623d2d7415c0806350f875114 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Install dependencies (needed for running Jest tests)
RUN corepack enable && yarn install

RUN mkdir -p /logs/verifier
