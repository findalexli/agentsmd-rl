FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/remix-run/remix.git /workspace/remix && \
    cd /workspace/remix && \
    git checkout 77567b453e4de0b2706cc9fa68c8f5d14e5361b3 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Install pnpm and project deps for route-pattern package
RUN corepack enable && \
    pnpm install --frozen-lockfile 2>&1 | tail -5 || true

# Ensure python3 + pytest available for test runner
RUN pip3 install --break-system-packages pytest pytest-json-ctrf 2>/dev/null || \
    python3 -m pip install pytest pytest-json-ctrf 2>/dev/null

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
