FROM node:24-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir pytest==8.3.4

WORKDIR /workspace

ARG REMIX_BASE_COMMIT=a2245eab8257758f5e323a5a4e3c89386568e3bb

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git remix \
    && cd remix \
    && git -c advice.detachedHead=false checkout ${REMIX_BASE_COMMIT} \
    && git checkout -B main \
    && git -c user.email=task@local.test -c user.name=task \
           commit --allow-empty -m "task base"

WORKDIR /workspace/extractor

RUN npm init -y >/dev/null \
    && npm pkg set type=module >/dev/null \
    && npm install --silent --no-audit --no-fund \
        tsx@4.20.6 \
        vitest@4.0.15

COPY vitest-stub.mjs /workspace/extractor/vitest-stub.mjs
COPY route-pattern-stub.mjs /workspace/extractor/route-pattern-stub.mjs
COPY loader.mjs /workspace/extractor/loader.mjs
COPY extract.mjs /workspace/extractor/extract.mjs

RUN mkdir -p /logs/verifier

WORKDIR /workspace/remix
