FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone next.js at the base commit (before the fix)
# Use init+fetch to avoid downloading the default branch first (repo is very large)
RUN git init /workspace/next.js \
    && cd /workspace/next.js \
    && git remote add origin https://github.com/vercel/next.js.git \
    && git fetch --depth=1 origin b6ff1f6079694da08af88cec5cac7381e22cea10 \
    && git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

# Configure git
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"