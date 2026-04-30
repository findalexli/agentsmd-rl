FROM node:22.22-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN pip3 install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset \
    && cd /workspace/superset \
    && git checkout 9fe3f634ec611713e6eb50d5db72faac2dc3ddcf

WORKDIR /workspace/superset/superset-frontend

ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN npm ci --no-audit --no-fund --prefer-offline 2>&1 | tail -5

WORKDIR /workspace/superset

RUN mkdir -p /logs/verifier
