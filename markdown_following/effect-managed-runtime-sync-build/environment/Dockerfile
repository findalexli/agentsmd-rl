FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g --silent pnpm@10.17.1

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/Effect-TS/effect.git effect \
    && cd effect \
    && git checkout dd4cf4b119592e670ad9347091bdec8a9c6c3422

WORKDIR /workspace/effect

RUN pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier
