FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git python3 python3-pip ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g yarn@1

RUN git clone --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout 1e3152365df2f7a23a5ad947e83f40914413be16 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

RUN yarn install --frozen-lockfile

RUN mkdir -p /logs/verifier
