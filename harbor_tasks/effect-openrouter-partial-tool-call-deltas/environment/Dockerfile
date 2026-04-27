FROM node:22.13.1-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NPM_CONFIG_FUND=false
ENV NPM_CONFIG_AUDIT=false
ENV CI=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      ca-certificates \
      python3 \
      python3-pip \
      python3-venv \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir \
      pytest==8.3.4 \
      pytest-json-ctrf==0.4.1

RUN npm install -g pnpm@10.17.1

ENV WORKDIR=/workspace
WORKDIR ${WORKDIR}

ARG REPO_URL=https://github.com/Effect-TS/effect.git
ARG BASE_COMMIT=aa473938a53d07837e84935329f4891a7d591c3b

RUN git clone --filter=blob:none ${REPO_URL} effect \
    && cd effect \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/effect

RUN pnpm install --filter "@effect/ai-openrouter..." --frozen-lockfile \
    && pnpm store prune || true

RUN mkdir -p /logs/verifier
