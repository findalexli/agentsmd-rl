FROM node:22-slim

WORKDIR /workspace

# Install Python 3 and pip (no recommends to avoid pulling in build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@9

# Clone the repo
RUN git clone --filter=blob:none --no-checkout https://github.com/continuedev/continue.git /workspace/continue
WORKDIR /workspace/continue
RUN git checkout f048649b1705bd21354b8a3554e92719d9c95cb8

# Install dependencies for openai-adapters
WORKDIR /workspace/continue/packages/openai-adapters
RUN pnpm install --no-frozen-lockfile \
    && pnpm add @aws-sdk/token-providers typescript@5.6.3 tsx@4

# Install pytest
RUN pip install --break-system-packages pytest pytest-timeout

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/continue