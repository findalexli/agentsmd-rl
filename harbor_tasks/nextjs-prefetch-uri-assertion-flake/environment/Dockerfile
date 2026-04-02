FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest at build time so verifier doesn't waste timeout on it
RUN pip3 install --break-system-packages pytest pytest-json-ctrf

# Clone repo at exact base commit (before the fix)
RUN git init /repo \
    && cd /repo \
    && git remote add origin https://github.com/vercel/next.js.git \
    && git fetch --depth=1 origin 138092696c355fa38ec8409e7f2c6c67c97e4f6b \
    && git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git user for patches
RUN git config user.email "test@test.com" && \
    git config user.name "Test"
