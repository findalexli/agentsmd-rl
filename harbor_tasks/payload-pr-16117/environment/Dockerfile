FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm@10.27.0

RUN pip install --break-system-packages pytest

WORKDIR /workspace

# Clone the repo
RUN git clone --filter=blob:none --no-checkout https://github.com/payloadcms/payload.git payload
WORKDIR /workspace/payload
RUN git checkout 3da805fb087a1fd2e9452d1ecaa3f5411cb9c57f

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build only what's needed for the next package with limited memory
WORKDIR /workspace/payload
RUN pnpm turbo build --filter=@payloadcms/ui --filter=@payloadcms/next --filter=payload --concatenate-output --no-cache --memory-limit=1g 2>&1 | tail -20 || true

RUN mkdir -p /logs/verifier

ENV NODE_OPTIONS="--no-deprecation --no-experimental-strip-types"
ENV NODE_NO_WARNINGS=1
ENV TURBO_FORCE=true