FROM node:22.13.1-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH
ENV CI=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.39.5-0+deb12u2 \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-ctrf==0.4.1

ENV COREPACK_INTEGRITY_KEYS=0
RUN corepack enable && corepack prepare pnpm@10.17.1 --activate

WORKDIR /workspace

ARG REPO_URL=https://github.com/Effect-TS/effect.git
ARG BASE_COMMIT=12b1f1eadf649e30dec581b7351ba3abb12f8004

RUN git clone --filter=blob:none "$REPO_URL" effect \
    && cd effect \
    && git checkout "$BASE_COMMIT" \
    && git config user.email "agent@example.com" \
    && git config user.name "agent"

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
