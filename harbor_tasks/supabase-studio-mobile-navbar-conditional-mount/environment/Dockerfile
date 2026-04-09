FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (monorepo, use filter=blob:none)
RUN git clone --filter=blob:none https://github.com/supabase/supabase.git /workspace/supabase && \
    cd /workspace/supabase && \
    git checkout bb66ba884c52443d964df4eb7567ba35a73a5abc && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Install minimal deps for Studio
RUN cd apps/studio && npm install 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
