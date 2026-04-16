FROM node:22-slim

RUN apt-get update && apt-get install -y git python3 python3-pip

WORKDIR /workspace

# Clone the repo at the base commit
RUN git clone --filter=blob:none --no-checkout https://github.com/withastro/astro.git /workspace/withastro-astro && \
    cd /workspace/withastro-astro && \
    git checkout 6b6751d85a6dfaf751919675d61eea16da9a7a26

# Install pnpm globally
RUN npm install -g pnpm

WORKDIR /workspace/withastro-astro

# Install dependencies (only what's needed for tests)
RUN pnpm install --frozen-lockfile

# Install pytest for running tests
RUN pip3 install --break-system-packages pytest

# Note: Building the full monorepo requires extensive dependencies.
# Tests check source code directly, so full build is not needed in Docker.
# The solve.sh will rebuild after applying the fix.

# Create logs directory
RUN mkdir -p /logs/verifier
