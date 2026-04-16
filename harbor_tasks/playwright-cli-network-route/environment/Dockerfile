FROM node:22-slim

# Install Python and required tools for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone playwright repo at base commit
# Base commit: 824f63da57edf990c6eeab6301d5f1b65dcb4ca8
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git checkout 824f63da57edf990c6eeab6301d5f1b65dcb4ca8

WORKDIR /workspace/playwright

# Install dependencies (skip playwright browser download for this task)
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
RUN npm ci --silent || npm install --silent

# Verify the skill file exists at base commit
RUN test -f .claude/skills/playwright-mcp-dev/SKILL.md && \
    echo "SKILL.md found at base commit"
