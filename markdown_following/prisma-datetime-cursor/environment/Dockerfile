FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PNPM_HOME=/usr/local/pnpm \
    PATH=/usr/local/pnpm:$PATH \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-venv \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH=/opt/venv/bin:$PATH

RUN npm install -g pnpm@10.15.1

WORKDIR /workspace

RUN git init /workspace/prisma && \
    cd /workspace/prisma && \
    git remote add origin https://github.com/prisma/prisma.git && \
    git fetch --depth=1 origin f8e742a8de6878a206d8493b61d911dac97e11df && \
    git checkout FETCH_HEAD

WORKDIR /workspace/prisma

RUN pnpm install --ignore-scripts \
        --filter "@prisma/client-engine-runtime..." \
        --include-workspace-root

RUN pnpm --filter "@prisma/client-engine-runtime^..." build

RUN mkdir -p /logs/verifier
