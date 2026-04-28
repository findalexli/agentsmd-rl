FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive \
    TURBO_TELEMETRY_DISABLED=1 \
    DO_NOT_TRACK=1 \
    CI=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

RUN npm install -g pnpm@9.6.0 turbo@2.8.11

WORKDIR /workspace
RUN git init /workspace/nextjs && \
    cd /workspace/nextjs && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin 46761a321042e8ac1863f4cfc8d73d527956e181 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/nextjs

RUN mkdir -p /logs/verifier
