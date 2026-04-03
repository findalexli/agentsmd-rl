FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin b2462694441412ad209c361dfa87f3f37a3d29f3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Tests extract _is_mistral_native_format via AST and exec it with stdlib
# only (os, re) — no need to install sglang or its heavy deps (torch, triton).

# Configure git user for any patch operations
RUN git config user.email "test@test.com" && git config user.name "Test"

# tests/ and solution/ are bind-mounted at runtime