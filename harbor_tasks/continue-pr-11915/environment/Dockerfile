FROM node:22-slim

WORKDIR /workspace

# Install python3 and pip for pytest runner (no exact version pins for compatibility)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone repo
RUN git clone --filter=blob:none --depth=1 https://github.com/continuedev/continue.git

WORKDIR /workspace/continue

# Checkout base commit (parent of merge)
RUN git checkout 16a540c3378b833931429db9bcb3ce7c98bd7a36

# Install monorepo root deps (minimal)
RUN npm install --ignore-scripts 2>&1 | tail -3

# Install packages that core depends on (resolve file: deps)
WORKDIR /workspace/continue/packages/config-yaml
RUN npm install --ignore-scripts 2>&1 | tail -3

WORKDIR /workspace/continue/packages/fetch
RUN npm install --ignore-scripts 2>&1 | tail -3

WORKDIR /workspace/continue/packages/llm-info
RUN npm install --ignore-scripts 2>&1 | tail -3

WORKDIR /workspace/continue/packages/openai-adapters
RUN npm install --ignore-scripts 2>&1 | tail -3

WORKDIR /workspace/continue/packages/terminal-security
RUN npm install --ignore-scripts 2>&1 | tail -3

# Install core package
WORKDIR /workspace/continue/core
RUN npm install --ignore-scripts 2>&1 | tail -3

# Install tsx for running TypeScript directly
RUN npm install --ignore-scripts tsx 2>&1 | tail -3

# Pin pytest for the test runner
RUN pip3 install pytest==8.3.4 --break-system-packages

# Create logs dir
RUN mkdir -p /logs/verifier

WORKDIR /workspace