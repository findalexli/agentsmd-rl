FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set up git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# VS Code needs Python 3 for some build tasks
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Clone VS Code at the pre-fix commit
WORKDIR /workspace
ARG BASE_COMMIT=837894c2410fb23371e591be89f64f9a89f73efe
RUN git clone --depth 1 https://github.com/microsoft/vscode.git vscode && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Clean git history for smaller image
RUN cd /workspace/vscode && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot at base commit"

# Install npm dependencies (but skip native builds where possible)
# We mainly need TypeScript compilation support
WORKDIR /workspace/vscode
RUN npm ci --ignore-scripts --prefix build || true

# Create verifier log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
