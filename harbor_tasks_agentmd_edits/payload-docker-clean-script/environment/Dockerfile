FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm and Docker CLI with compose plugin
RUN npm install -g pnpm && \
    apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/lib/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose || true

# Clone repo at base commit and install dependencies
RUN git clone --depth=1 https://github.com/payloadcms/payload.git /workspace/payload && \
    cd /workspace/payload && \
    git fetch --depth=1 origin a188556e99d94c96266671b2129e5c8cb05e46a5 && \
    git checkout a188556e99d94c96266671b2129e5c8cb05e46a5 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Install dependencies (needed for repo_tests)
RUN pnpm install --frozen-lockfile || pnpm install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
