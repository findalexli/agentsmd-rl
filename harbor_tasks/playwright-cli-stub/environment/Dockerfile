FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone Playwright at base commit (shallow clone for speed)
ARG BASE_COMMIT=23b2c1599085bb6dad0f8fb916b631e3cb50ba4b
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies (use npm ci for reproducibility)
WORKDIR /workspace/playwright
RUN npm ci

# Build the project
RUN npm run build

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/playwright
