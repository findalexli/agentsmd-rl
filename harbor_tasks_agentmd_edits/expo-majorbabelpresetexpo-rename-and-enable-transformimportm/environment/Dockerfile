FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone expo at base commit (shallow snapshot for speed)
RUN git init /workspace/expo && \
    cd /workspace/expo && \
    git remote add origin https://github.com/expo/expo.git && \
    git fetch --depth=1 origin e7f9f0359afa2414576dd57c9166272e3b64c5df && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/expo

# Install @babel/core in babel-preset-expo dir for behavioral testing
RUN cd packages/babel-preset-expo && \
    npm install --no-save @babel/core@"^7.26.0" 2>&1 | tail -3

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
