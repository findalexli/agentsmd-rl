FROM node:22.22.0-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /workspace

RUN git init superset \
    && cd superset \
    && git config advice.detachedHead false \
    && git remote add origin https://github.com/apache/superset.git \
    && git fetch --depth 1 origin 7a243d329ef7457bbb131808a3132c2ea7bf5037 \
    && git checkout 7a243d329ef7457bbb131808a3132c2ea7bf5037

WORKDIR /workspace/superset/superset-frontend

RUN npm ci --no-audit --no-fund --prefer-offline --ignore-scripts \
    && npm cache clean --force

WORKDIR /workspace/superset

RUN mkdir -p /logs/verifier
