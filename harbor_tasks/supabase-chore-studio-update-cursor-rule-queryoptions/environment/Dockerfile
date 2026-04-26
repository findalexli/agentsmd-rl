FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Pre-install test runner deps so test.sh doesn't need network
RUN pip3 install --break-system-packages pytest pytest-json-ctrf pyyaml

# Clone repo at base commit (large monorepo — use blob filter)
RUN git init /workspace/supabase && \
    cd /workspace/supabase && \
    git remote add origin https://github.com/supabase/supabase.git && \
    git fetch --depth=1 origin 11d4da6c4b6d282c1d829a4786a342468472a698 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent" && \
    find .cursor -name '*.md' -exec sed -i "s/\xe2\x80\x99/'/g" {} + && \
    git add -A && git commit -m "normalize unicode quotes" --allow-empty

WORKDIR /workspace/supabase

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
