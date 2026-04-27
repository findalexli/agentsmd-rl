FROM node:22.14.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3=3.11.2-1+b1 \
        python3-pip \
        python3-venv \
        ca-certificates \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pyenv \
 && /opt/pyenv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1 \
        pyyaml==6.0.2
ENV PATH="/opt/pyenv/bin:${PATH}"

WORKDIR /workspace
RUN curl -fsSL "https://codeload.github.com/cloudflare/workers-sdk/legacy.tar.gz/525a46bca7c9a8a57972ac152ab9c400df0bf186" -o /tmp/repo.tar.gz \
 && mkdir -p /workspace/workers-sdk \
 && tar xzf /tmp/repo.tar.gz -C /workspace/workers-sdk --strip-components=1 \
 && rm /tmp/repo.tar.gz

WORKDIR /test-runner
COPY runner/package.json ./package.json
COPY runner/vitest.config.ts ./vitest.config.ts
COPY runner/tsconfig.json ./tsconfig.json
COPY runner/test ./test
RUN npm install --no-audit --no-fund --include=optional

RUN mkdir -p /logs/verifier

WORKDIR /workspace
