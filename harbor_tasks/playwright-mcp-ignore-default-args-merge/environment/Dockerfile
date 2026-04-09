FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow fetch — monorepo is large)
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin c7d0163db5580377d6e94953d593adb799d32c22 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
