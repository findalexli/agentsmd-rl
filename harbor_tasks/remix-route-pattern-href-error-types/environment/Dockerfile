FROM node:24-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest==8.3.4 --break-system-packages

RUN npm install -g pnpm@10.26.0

ENV CI=true

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 96c3f0c095dc8de98543af55df0b9400656f961b && \
    pnpm install --filter @remix-run/route-pattern...

WORKDIR /workspace/remix/packages/route-pattern

RUN mkdir -p /logs/verifier
