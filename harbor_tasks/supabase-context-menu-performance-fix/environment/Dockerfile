FROM node:22-slim
# Node/TS repo - need python3 for pytest test runner

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (supabase monorepo is large)
RUN git clone --depth=1000 https://github.com/supabase/supabase.git /workspace/supabase && \
    cd /workspace/supabase && \
    git checkout 2af6b3eaec65971a8fa6986afad44d6581075ac5 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Install only the studio app dependencies needed for tests
# Need to install at monorepo root for dependencies to resolve
RUN cd /workspace/supabase && \
    corepack enable pnpm && \
    pnpm install --frozen-lockfile --filter=studio --filter=@supabase/ui --filter=@supabase/ui-patterns 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
