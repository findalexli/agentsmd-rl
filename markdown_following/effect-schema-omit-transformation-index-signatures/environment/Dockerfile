FROM node:23.7.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/pnpm
ENV PATH=/pnpm:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

RUN python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1 pyyaml==6.0.2

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/effect-ts/effect.git effect \
    && cd effect \
    && git checkout 4d97a61a15b9dd6a0eece65b8f0c035e16d42ada

WORKDIR /workspace/effect
RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
