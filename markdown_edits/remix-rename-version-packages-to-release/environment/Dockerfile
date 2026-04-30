FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm globally
RUN npm install -g pnpm

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 130fbdc7b808a2d313363458dabc00caf036f482 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Install dependencies (needed for pnpm lint, typecheck, etc.)
RUN pnpm install --frozen-lockfile

# Pre-create mount point and set permissions
RUN mkdir -p /logs/verifier && chmod 777 /logs/verifier

# Set up pnpm environment
ENV PNPM_HOME="/root/.local/share/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}"

WORKDIR /workspace/remix
