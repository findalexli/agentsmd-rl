FROM node:22-slim

# Install python3 and pnpm
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Clone repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router
ARG BASE_COMMIT=e1b019ccb84ba2a5c60d36adae2440ac9f5bc34f
RUN git checkout ${BASE_COMMIT}

# Install dependencies
RUN pnpm install

# Build packages (needed for type checking)
RUN pnpm build:all

# Setup log directory
RUN mkdir -p /logs/verifier
