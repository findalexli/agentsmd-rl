# syntax=docker/dockerfile:1

FROM node:18-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and git for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone express-async-handler repo at the base commit
WORKDIR /workspace
RUN git clone --depth=1 --filter=blob:none \
    https://github.com/expressjs/express-async-handler.git && \
    cd express-async-handler && \
    git fetch --depth=1 origin 3b71cf2842d60d2f200361db42f238ce43d6e7eb && \
    git checkout 3b71cf2842d60d2f200361db42f238ce43d6e7eb

WORKDIR /workspace/express-async-handler

# Install dependencies
RUN npm install

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/express-async-handler
