FROM node:22-slim

# Install python3 for pytest, git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git patch \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm (repo uses pnpm@10.28.1)
RUN corepack enable && corepack prepare pnpm@10.28.1 --activate

# Clone repo at base commit (parent of merge commit)
WORKDIR /workspace
RUN git init /workspace/civitai && \
    cd /workspace/civitai && \
    git remote add origin https://github.com/civitai/civitai.git && \
    git fetch --depth=1 origin 47c3beedb50993e5f410e241e4940131bba9afb2 && \
    git checkout FETCH_HEAD

# Install dependencies for typecheck/lint CI commands
WORKDIR /workspace/civitai
RUN pnpm install 2>&1 | tail -5

# Generate Prisma client (needed for typecheck)
RUN pnpm run db:generate 2>&1 | tail -5 || true

# Install pytest (pinned)
RUN pip3 install --break-system-packages pytest==8.3.4

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/civitai
