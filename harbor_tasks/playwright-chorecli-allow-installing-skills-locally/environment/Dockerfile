FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install system dependencies including git, python3 (for tests), and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip \
        pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Install pytest for testing
RUN pip3 install pytest --break-system-packages

# Clone repo at base commit (6a928b02f4de1efc633a8fae0331cd1fa821950e)
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 6a928b02f4de1efc633a8fae0331cd1fa821950e && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install dependencies (this is needed for TypeScript compilation)
RUN npm ci --ignore-scripts 2>&1 || npm install --ignore-scripts 2>&1 || true

# Build the packages once to ensure compiled output exists
RUN npm run build 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
