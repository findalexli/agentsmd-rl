FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
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

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace
RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin d4ed885bb94b45e315bd275a44a9e472ef6074f4 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect
RUN pnpm install --frozen-lockfile --prefer-offline

RUN mkdir -p /logs/verifier

ENV CI=true
WORKDIR /workspace/effect
