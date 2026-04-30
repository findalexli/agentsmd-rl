FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive \
    NODE_OPTIONS="--max-old-space-size=4096" \
    CI=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
        bash \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pyenv \
    && /opt/pyenv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5
ENV PATH="/opt/pyenv/bin:${PATH}"

WORKDIR /workspace

ARG REPO_URL=https://github.com/ant-design/ant-design.git
ARG BASE_COMMIT=e703cb131eb208a7cd697eb5503955a5e4314e29

RUN git clone --filter=blob:none "${REPO_URL}" ant-design \
    && cd ant-design \
    && git checkout "${BASE_COMMIT}"

WORKDIR /workspace/ant-design

RUN npm install --legacy-peer-deps --no-audit --no-fund --prefer-offline 2>&1 | tail -30

RUN npm run version

RUN mkdir -p /logs/verifier
