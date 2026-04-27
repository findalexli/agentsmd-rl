FROM node:22.11-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      ca-certificates \
      python3 \
      python3-pip \
      python3-venv \
      curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --no-cache-dir \
      pytest==8.3.4 \
      pyyaml==6.0.2

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/Effect-TS/effect.git effect

WORKDIR /workspace/effect
RUN git checkout f6b0960bf3184109920dfed16ee7dfd7d67bc0f2

ENV PNPM_HOME=/root/.pnpm-store
RUN pnpm config set store-dir /root/.pnpm-store

RUN pnpm install --frozen-lockfile --ignore-scripts

RUN mkdir -p /logs/verifier
