FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the repo at base commit
WORKDIR /workspace
ARG BASE_COMMIT=fb1e8b20f9f157ad46aeade73b69c2b409d9c662
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router
WORKDIR /workspace/router
RUN git checkout ${BASE_COMMIT}

# Install dependencies
RUN pnpm install

WORKDIR /workspace/router
