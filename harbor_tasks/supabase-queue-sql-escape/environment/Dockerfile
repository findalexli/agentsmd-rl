FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# tsx for running TypeScript directly in tests
RUN npm install -g tsx

# Clone repo at base commit (partial clone for large monorepo)
RUN git clone --filter=blob:none https://github.com/supabase/supabase.git /workspace/supabase && \
    cd /workspace/supabase && \
    git checkout 273102323d2959bf5e24678a3388409e91e2ccb4 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
