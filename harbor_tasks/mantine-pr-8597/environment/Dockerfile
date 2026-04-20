FROM node:20-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages pytest==8.3.4

WORKDIR /workspace

# Clone repo (shallow)
RUN git clone --depth=1 https://github.com/mantinedev/mantine.git repo 2>/dev/null || \
    git clone https://github.com/mantinedev/mantine.git repo

WORKDIR /workspace/repo

# Checkout base commit
RUN git fetch --depth=1 origin b7075e17ccce448cebda8cde98096b8dde633963 && \
    git checkout b7075e17ccce448cebda8cde98096b8dde633963

# Install dependencies
RUN corepack enable && yarn install

# Create log directory
RUN mkdir -p /logs/verifier
