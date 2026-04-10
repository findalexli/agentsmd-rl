FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update &&     apt-get install -y --no-install-recommends         git curl ca-certificates python3 python3-pip python3-venv &&     rm -rf /var/lib/apt/lists/*

# Install tsx for running TypeScript directly
RUN npm install -g tsx semver

# Install pnpm
RUN npm install -g pnpm

# Clone repo at base commit (before tag→channel rename)
RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix &&     cd /workspace/remix &&     git checkout 40a755c50f40ed444a928363beddd75e6edc1f52 &&     git config user.email "agent@test" &&     git config user.name "Agent"

WORKDIR /workspace/remix

# Install repo dependencies (needed for eslint and other tools)
RUN pnpm install --frozen-lockfile || pnpm install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
