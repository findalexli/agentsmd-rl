FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git python3 python3-pip ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone PostHog at base commit (pre-fix)
RUN git init /workspace/posthog && \
    cd /workspace/posthog && \
    git remote add origin https://github.com/PostHog/posthog.git && \
    git fetch --depth=1 origin 6ffa23dc367bd7935376dde246fdd7b986ebf8b8 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/posthog

# Install pnpm via corepack (version from package.json packageManager field)
# Then install only the MCP service and its transitive workspace deps
RUN corepack enable && \
    corepack prepare pnpm@10.29.3 --activate && \
    (pnpm install --filter @posthog/mcp... --frozen-lockfile || \
     pnpm install --filter @posthog/mcp... --no-frozen-lockfile)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
