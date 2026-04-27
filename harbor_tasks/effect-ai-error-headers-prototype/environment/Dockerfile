FROM node:22.13.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CI=true
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.17.1

RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

WORKDIR /workspace

RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin f6b0960bf3184109920dfed16ee7dfd7d67bc0f2 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile --prefer-offline 2>&1 | tail -20

RUN mkdir -p /logs/verifier
