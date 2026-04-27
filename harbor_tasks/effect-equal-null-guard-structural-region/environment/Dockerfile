FROM node:22.12.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CI=true
ENV PNPM_HOME=/pnpm
ENV PATH=/pnpm:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

RUN npm install -g pnpm@10.17.1

WORKDIR /workspace

RUN git init /workspace/effect && \
    cd /workspace/effect && \
    git remote add origin https://github.com/Effect-TS/effect.git && \
    git fetch --depth=1 origin 5c80e578bd95e0cf6fceffc72fa0b130ca11ec8e && \
    git checkout FETCH_HEAD

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile --ignore-scripts

RUN mkdir -p /logs/verifier
