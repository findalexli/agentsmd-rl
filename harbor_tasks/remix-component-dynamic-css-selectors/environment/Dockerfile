FROM node:24.11.0-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git=1:2.39.5-0+deb12u2 \
    python3 \
    python3-pip \
    python3-venv \
    && ln -sf /usr/bin/pip3 /usr/bin/pip \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g tsx@4.19.2

ENV PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /workspace/remix

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix \
    && git checkout 69fb670d88798e2abe3064f9c1dff4946aba0c2b

RUN mkdir -p /logs/verifier
