FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone — supabase monorepo is large
RUN git init /workspace/supabase && \
    cd /workspace/supabase && \
    git remote add origin https://github.com/supabase/supabase.git && \
    git fetch --depth=1 origin fba5a8a001b0fb775e3e8054e57b1c7a9cba8a0c && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
