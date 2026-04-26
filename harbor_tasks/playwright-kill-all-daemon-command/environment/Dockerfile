FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip procps && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pytest pytest-json-ctrf

RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 8710e613f8297cebe33c4f6a745999ab4e4907aa && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install Node deps without downloading browsers
RUN npm ci --ignore-scripts

RUN mkdir -p /logs/verifier
