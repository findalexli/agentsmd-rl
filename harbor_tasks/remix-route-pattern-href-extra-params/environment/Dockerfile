FROM node:24-slim

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable

WORKDIR /workspace/remix

RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix \
    && git checkout 7a028b5a1cccb5b231f6b908da2aa06a95000a7f \
    && pnpm install --frozen-lockfile

RUN mkdir -p /logs/verifier

# Pre-install pytest in a venv so tests don't need network
RUN python3 -m venv /opt/pytest-venv && /opt/pytest-venv/bin/pip install pytest==8.3.4
ENV PATH="/opt/pytest-venv/bin:$PATH"

WORKDIR /workspace/remix/packages/route-pattern
