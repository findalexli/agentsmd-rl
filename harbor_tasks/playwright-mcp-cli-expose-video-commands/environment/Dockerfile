FROM nikolaik/python-nodejs:python3.12-nodejs22-slim

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone Playwright repo at base commit (shallow clone for speed)
WORKDIR /workspace
RUN git clone --depth=1 --filter=blob:none \
    https://github.com/microsoft/playwright.git playwright \
    && cd playwright \
    && git fetch --depth=1 origin 8c99ff19b8e03ab21cec344d8b2f1d149d4040c7 \
    && git checkout 8c99ff19b8e03ab21cec344d8b2f1d149d4040c7

WORKDIR /workspace/playwright

# Install dependencies
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true

# Install pytest
RUN pip install pytest --no-cache-dir

ENV REPO=/workspace/playwright
