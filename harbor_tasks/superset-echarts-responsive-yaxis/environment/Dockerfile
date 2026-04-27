FROM node:20-trixie-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV CYPRESS_INSTALL_BINARY=0
ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN pip3 install --no-cache-dir \
        pytest==8.3.4

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout e6f1209318b8def92c27c09fed87b3538a10a36c

WORKDIR /workspace/superset/superset-frontend

RUN npm ci --no-audit --no-fund --prefer-offline --legacy-peer-deps 2>&1 | tail -50

RUN mkdir -p /logs/verifier
