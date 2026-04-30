FROM python:3.12-slim AS base

# Install only essential tools in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Install pytest
RUN pip install pytest --no-cache-dir

# Set up workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone Playwright repo at base commit
ARG BASE_COMMIT=23b12474a184466c5a83db49b7bcf4d45e970a26
RUN git clone --depth=1 https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/playwright

# Install only production npm dependencies
RUN npm ci && npm run build

RUN mkdir -p /logs/verifier
