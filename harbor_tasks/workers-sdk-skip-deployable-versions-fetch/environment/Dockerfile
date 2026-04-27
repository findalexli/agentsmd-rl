FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@9.12.0 --activate

RUN pip install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-ctrf==0.3.5

WORKDIR /workspace

RUN git init /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git remote add origin https://github.com/cloudflare/workers-sdk.git && \
    git fetch --depth=1 origin 9282493b11ba07bcadb981c2cfc255e8eb5b9b15 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/workers-sdk

# Skip the assert-git-version pre-test step that requires git tag tooling
# we don't need; we'll invoke vitest directly.
RUN pnpm install --filter wrangler... --frozen-lockfile 2>&1 | tail -20

RUN pnpm turbo build --filter wrangler 2>&1 | tail -20

# Reference (post-PR) version of the vitest test file. Baked into the
# image so test_outputs.py can copy it over the agent's checkout at test
# time, anchoring the snapshot expectations to the post-PR API.
COPY fixtures/versions.deploy.test.ts.post /opt/fixtures/versions.deploy.test.ts.post

RUN mkdir -p /logs/verifier

WORKDIR /workspace/workers-sdk
