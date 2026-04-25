FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/supabase/supabase.git /workspace/supabase && \
    cd /workspace/supabase && \
    git checkout e7bec24021de77053a9b9b05c06ab17789f1269b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/supabase

# Install typescript for syntax checking
RUN npm install -g typescript

# Verifier output directory
RUN mkdir -p /logs/verifier

# Install pnpm globally for repo_tests
RUN npm install -g pnpm

# Pre-install dependencies for faster test execution
RUN cd /workspace/supabase && pnpm install --ignore-scripts
