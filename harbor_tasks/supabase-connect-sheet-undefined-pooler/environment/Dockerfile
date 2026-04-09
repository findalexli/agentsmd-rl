FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install python3 for test runner, git for cloning, and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/supabase/supabase.git /workspace/supabase && \
    cd /workspace/supabase && \
    git checkout 042248fd6d70bc56d49db6c16462a8cc237c2945 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Install minimal deps for TypeScript checking
RUN npm install -g typescript @types/node

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
