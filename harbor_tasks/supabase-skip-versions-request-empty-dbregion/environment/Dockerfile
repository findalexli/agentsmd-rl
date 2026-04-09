FROM node:22-slim
# Need python3 for pytest test runner

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo with partial clone (blobless) to support checking out older commits
RUN git clone --filter=blob:none https://github.com/supabase/supabase.git /workspace/supabase && \
    cd /workspace/supabase && \
    git checkout b5326ce3b2130bd89689606cb2290501832d910f && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Install pnpm and dependencies for the studio app (needed for type checking)
RUN npm install -g pnpm && \
    pnpm install --filter=studio --frozen-lockfile || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
