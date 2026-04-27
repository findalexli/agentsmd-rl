FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        curl \
        python3 \
        python3-pip \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5

RUN npm install -g pnpm@9.12.0

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git \
    && cd workers-sdk \
    && git checkout 17a57e641798dca0b298bd91dcdcef6be30d38b6

WORKDIR /workspace/workers-sdk

# Install only the workspace deps required by miniflare (transitive)
RUN pnpm install --filter "miniflare..." --frozen-lockfile --prefer-offline

# Build miniflare AND its transitive workspace deps (note `...`)
RUN pnpm --filter "miniflare..." run build

RUN mkdir -p /logs/verifier
