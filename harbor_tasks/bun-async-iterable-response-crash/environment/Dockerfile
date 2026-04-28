FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install bun-v1.3.11 — the last release before PR #28457 was merged on 2026-03-25.
# This version has the async-iterable Response body crash bug.
RUN curl -fsSL https://bun.sh/install | bash -s -- bun-v1.3.11
ENV PATH="/root/.bun/bin:${PATH}"

# Clone bun at the base commit (BEFORE the fix)
RUN git init /workspace/bun && \
    cd /workspace/bun && \
    git remote add origin https://github.com/oven-sh/bun.git && \
    git fetch --depth=1 origin 9ead1e121d5cca2eaddad66d439ab3c0a74225f2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun
