FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        pytest-metadata==3.1.1

ARG REPO_URL=https://github.com/apache/superset.git
ARG BASE_COMMIT=5138aa2c114fd74a13cfce6f713470b25b542a27

WORKDIR /workspace

RUN git clone --filter=blob:none --no-checkout ${REPO_URL} superset \
    && cd superset \
    && git sparse-checkout init --cone \
    && git sparse-checkout set superset-frontend \
    && git -c advice.detachedHead=false checkout ${BASE_COMMIT}

WORKDIR /workspace/superset/superset-frontend

RUN npm ci --no-audit --no-fund

RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
