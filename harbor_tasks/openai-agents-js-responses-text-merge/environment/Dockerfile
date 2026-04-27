FROM node:22.12.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.14.0

ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN pip3 install --no-cache-dir pytest==8.3.4

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git openai-agents-js \
    && cd openai-agents-js \
    && git checkout 2260e211926624c0bcd89497a8b180724b14d720

WORKDIR /workspace/openai-agents-js

ENV CI=1
ENV HUSKY=0
RUN pnpm install --frozen-lockfile --ignore-scripts

RUN pnpm -F '@openai/*' -r prebuild && pnpm exec tsc-multi

RUN mkdir -p /logs/verifier
