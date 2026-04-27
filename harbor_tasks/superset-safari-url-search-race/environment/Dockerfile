FROM node:22.12.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_OPTIONS="--max-old-space-size=8192"

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip==24.3.1 \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /workspace

ARG SUPERSET_REPO_URL=https://github.com/apache/superset.git
ARG SUPERSET_BASE_COMMIT=8559786cc2994d731300e5e53c58e2246adfac72

RUN git clone --filter=blob:none "${SUPERSET_REPO_URL}" /workspace/superset \
    && cd /workspace/superset \
    && git checkout "${SUPERSET_BASE_COMMIT}" \
    && git config user.email "scaffold@example.com" \
    && git config user.name "Scaffold"

WORKDIR /workspace/superset/superset-frontend

RUN npm ci --no-audit --no-fund --prefer-offline 2>&1 | tail -50

WORKDIR /workspace/superset

RUN mkdir -p /logs/verifier
