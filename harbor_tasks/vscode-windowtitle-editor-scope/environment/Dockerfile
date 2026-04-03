FROM node:22-slim

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/vscode

# Clone VS Code repo at base commit (pre-fix)
ARG BASE_COMMIT=c2016b08f5d48a676858f04907c2b1c10ab03a44
RUN git init && \
    git remote add origin https://github.com/microsoft/vscode.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies (minimal - only what's needed for type checking)
RUN npm ci --ignore-scripts 2>&1 | tail -20 || npm install --ignore-scripts 2>&1 | tail -20

# Configure git user for any potential patch operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
