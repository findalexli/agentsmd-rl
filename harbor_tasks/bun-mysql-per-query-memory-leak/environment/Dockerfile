FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 9a27ef75697d713dba18b7a9762308197014ecca && \
    git checkout FETCH_HEAD && \
    git config user.name "test" && \
    git config user.email "test@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /repo