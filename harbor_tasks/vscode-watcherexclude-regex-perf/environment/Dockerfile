FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone vscode repo at base commit
ARG BASE_COMMIT=002f2d99e814b4068447558eef47ac8977d1c05a
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize snapshot - remove .git history but keep the code
WORKDIR /workspace/vscode
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for TypeScript checking
RUN npm ci --ignore-scripts --prefer-offline 2>/dev/null || \
    npm install --ignore-scripts --prefer-offline || true

WORKDIR /workspace/vscode

# Create logs directory
RUN mkdir -p /logs/verifier
