FROM node:24-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git ca-certificates build-essential \
    && pip install --break-system-packages pytest==8.3.4 pyyaml==6.0.2 \
    && npm install -g typescript@5.7.3 prettier@3.4.2 pnpm@10.32.1 \
    && rm -rf /var/lib/apt/lists/*

ENV NODE_PATH=/usr/local/lib/node_modules

RUN mkdir -p /logs/verifier

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/remix-run/remix.git remix
WORKDIR /workspace/remix
RUN git checkout 87447287f87d29f394c71c1859d293f78b69cdca
RUN pnpm install --frozen-lockfile
