FROM node:18-alpine

# Install Python and git
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git

# Create working directory
WORKDIR /workspace

# Clone playwright repo at base commit
ARG BASE_COMMIT=71e5079b735eda08a72b0fac58a3dd02fde6bb9f
RUN git clone --filter=blob:none --depth=100 https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies and build
WORKDIR /workspace/playwright
RUN npm ci && npm run build

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/playwright
