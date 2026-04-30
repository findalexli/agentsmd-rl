FROM node:22.13.1-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CI=1
ENV PRISMA_SKIP_POSTINSTALL_GENERATE=1
ENV PRISMA_SKIP_DOWNLOAD_BINARIES=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        curl \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        pyyaml==6.0.2
ENV PATH="/opt/venv/bin:${PATH}"

RUN npm install -g pnpm@10.15.1 --loglevel=error

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git init /workspace/prisma && \
    cd /workspace/prisma && \
    git remote add origin https://github.com/prisma/prisma.git && \
    git fetch --depth=1 origin 857400baec117a7acd8be8799fa285d146329a33 && \
    git checkout FETCH_HEAD \
    && git config user.email "task@local" \
    && git config user.name "task"

WORKDIR /workspace/prisma

RUN pnpm install --frozen-lockfile --ignore-scripts 2>&1 | tail -50

RUN pnpm --filter @prisma/debug \
        --filter @prisma/driver-adapter-utils \
        run build 2>&1 | tail -30

WORKDIR /workspace/prisma
