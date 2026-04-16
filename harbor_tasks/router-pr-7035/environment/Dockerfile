FROM node:22-slim

# Install pnpm, git, python3, and pytest
RUN npm install -g pnpm@10 && \
    apt-get update && \
    apt-get install -y git python3 python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --break-system-packages pytest

# Clone the repository
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 749e88b68e920b90cf034859c51e82609b3f891f

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Install publint and attw for package validation (needed by tests)
RUN pnpm add -w -D publint @arethetypeswrong/cli

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/router
