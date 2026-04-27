FROM node:20.20.0-trixie-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        git \
        ca-certificates \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pytest-venv \
    && /opt/pytest-venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

ENV PATH="/opt/pytest-venv/bin:${PATH}"

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/Infisical/infisical.git infisical
WORKDIR /workspace/infisical
RUN git checkout eb98c0780a16851e642c1a2f47a01c8548b5689a

WORKDIR /workspace/infisical/backend
RUN npm ci --no-audit --no-fund

RUN mkdir -p /logs/verifier

WORKDIR /workspace/infisical
