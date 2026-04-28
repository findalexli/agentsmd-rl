FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && pip3 install --break-system-packages pytest==8.3.4 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk /workspace/workers-sdk \
    && cd /workspace/workers-sdk \
    && git checkout 2363d485a67b8c5abdffd01eee1bd3eb6bd53b10

RUN mkdir -p /logs/verifier
WORKDIR /workspace/workers-sdk
