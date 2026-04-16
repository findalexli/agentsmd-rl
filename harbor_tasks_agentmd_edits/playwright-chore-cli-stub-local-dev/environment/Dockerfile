FROM node:22

# Install Python and git for testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=23b2c1599085bb6dad0f8fb916b631e3cb50ba4b
RUN git clone --filter=blob:none --depth=100 https://github.com/microsoft/playwright.git playwright \
    && cd playwright \
    && git checkout ${BASE_COMMIT}

# Install dependencies (skip playwright browser download - not needed for CLI tests)
WORKDIR /workspace/playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
RUN npm ci --ignore-scripts

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default workdir is the repo
WORKDIR /workspace/playwright
