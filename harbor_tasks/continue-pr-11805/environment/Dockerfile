FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none --depth=1 https://github.com/continuedev/continue.git continue

WORKDIR /workspace/continue
RUN git checkout d6259a73046775d90e2440117ee05cc439f26d04

# Install Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@9

# Install TypeScript globally for tsc command
RUN npm install -g typescript@5

# Install dependencies for openai-adapters package
WORKDIR /workspace/continue/packages/openai-adapters
RUN pnpm install

# Also install dependencies for core package
WORKDIR /workspace/continue
RUN pnpm install

# Install pytest for running tests
RUN pip install --no-cache-dir pytest==8.3.4

RUN mkdir -p /workspace/task && ln -s /tests /workspace/task/tests && ln -s /logs/verifier /workspace/task/logs

RUN mkdir -p /logs/verifier