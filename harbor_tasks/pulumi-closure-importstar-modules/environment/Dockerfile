FROM node:20-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates python3 python3-pip python3-venv \
        build-essential pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1 \
        pyyaml==6.0.2

RUN mkdir -p /logs/verifier

WORKDIR /workspace
RUN git init /workspace/pulumi && \
    cd /workspace/pulumi && \
    git remote add origin https://github.com/pulumi/pulumi.git && \
    git fetch --depth=1 origin 8a51e8bcf47a806b25a6c602fa6ae92f8296d97b && \
    git checkout FETCH_HEAD

WORKDIR /workspace/pulumi/sdk/nodejs
RUN yarn install --frozen-lockfile --network-timeout 600000

RUN yarn run tsc \
    && mkdir -p bin/proto \
    && cp -R proto/. bin/proto/ \
    && cp package.json bin/package.json \
    && cp -R vendor/. bin/vendor/

WORKDIR /workspace/pulumi
