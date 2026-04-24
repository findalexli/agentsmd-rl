FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

# Shallow clone at the base commit (parent of merge commit)
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin cb0d88f6e3e340216d478e0ba0c201ec23f7c15c && \
    git checkout FETCH_HEAD

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/next.js
RUN pip3 install pytest pytest-json-ctrf --break-system-packages
