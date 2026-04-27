FROM node:22.11.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH="$PNPM_HOME:$PATH"
ENV CI=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        curl \
        build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4

RUN npm install -g pnpm@10.17.1

ARG BASE_COMMIT=12b1f1eadf649e30dec581b7351ba3abb12f8004

RUN git clone --filter=blob:none https://github.com/Effect-TS/effect.git /workspace/effect \
 && cd /workspace/effect \
 && git checkout "${BASE_COMMIT}"

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
