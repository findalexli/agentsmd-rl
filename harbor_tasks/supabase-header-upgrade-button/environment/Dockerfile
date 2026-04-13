FROM node:22-slim
# Node/TS repo - need python3 for pytest test runner

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm globally
RUN npm install -g pnpm

# Clone repo at base commit (shallow fetch of specific commit for speed)
RUN git init /workspace/supabase && \
    cd /workspace/supabase && \
    git remote add origin https://github.com/supabase/supabase.git && \
    git fetch --depth=1 origin cccae29569c129e52178837d6d4662baa11f5986 && \
    git checkout FETCH_HEAD && \
    git checkout -b main && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Install dependencies for studio and common packages (needed for repo tests)
RUN pnpm install --frozen-lockfile --prefer-offline || pnpm install --prefer-offline

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
