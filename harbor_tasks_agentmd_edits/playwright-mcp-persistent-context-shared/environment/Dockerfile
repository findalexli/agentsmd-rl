FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow clone for reliability)
RUN git clone --depth=200 https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 114f3a296a78dfbc1eb6631bb358e9fe9b1677bb && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install dependencies
RUN npm ci

# Build the project
RUN npm run build

# Verifier output directory
RUN mkdir -p /logs/verifier
