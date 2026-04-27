FROM node:23.7.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.3.5

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

WORKDIR /workspace
RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin 4d97a61a15b9dd6a0eece65b8f0c035e16d42ada && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
