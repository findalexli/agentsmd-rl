FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV PNPM_HOME="/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm && pnpm config set store-dir /pnpm/store

# Clone repo at base commit (shallow clone for faster builds)
RUN git clone --filter=blob:none https://github.com/lobehub/lobe-chat.git /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git checkout be8903e70771ad1af43159c17ea62185eae180a2 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lobe-chat

# Install dependencies (this will be cached if package.json doesn't change)
RUN pnpm install --frozen-lockfile 2>&1 || pnpm install 2>&1 || true

# Pre-fetch TypeScript to speed up checks
RUN npm install -g typescript 2>&1 || true

# Install gh CLI for solve.sh
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && rm -rf /var/lib/apt/lists/*

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
