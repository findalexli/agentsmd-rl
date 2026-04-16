FROM node:22-alpine

# Install Python for pytest and git
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv \
    git

# Set up Python virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install pytest
RUN pip install --no-cache-dir pytest --break-system-packages 2>/dev/null || \
    pip install --no-cache-dir pytest

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone Playwright repo at base commit
WORKDIR /home/node
RUN git clone --depth=1 --filter=blob:none https://github.com/microsoft/playwright.git playwright

WORKDIR /home/node/playwright
RUN git fetch --depth=1 origin 08752e9a9be05e5d11173977c8651cf105c1aace && \
    git checkout 08752e9a9be05e5d11173977c8651cf105c1aace

# Install npm dependencies for the packages we need
WORKDIR /home/node/playwright/packages/playwright
RUN npm install 2>/dev/null || true

# Set final working directory
WORKDIR /home/node/playwright

# Verify Node and Python are available
RUN node --version && python3 --version
