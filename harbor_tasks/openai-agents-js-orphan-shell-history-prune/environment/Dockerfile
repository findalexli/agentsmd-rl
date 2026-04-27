FROM node:22.14.0-slim

# Install OS deps for git, build tools, and python3 (used by pytest test harness).
RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.* \
    ca-certificates \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pinned pytest in a virtualenv so PEP 668 does not block us.
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pytest==8.3.4

# Enable pnpm via corepack at the repository's pinned version.
RUN corepack enable && corepack prepare pnpm@10.30.3 --activate

# Clone the repo at the base commit (pre-fix).
WORKDIR /workspace
RUN git init /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git remote add origin https://github.com/openai/openai-agents-js.git && \
    git fetch --depth=1 origin 5f8646167f0ef281fe4f7fa691c8623b5db3db72 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/openai-agents-js

# Disable husky hooks (not needed inside the image).
ENV HUSKY=0

# Install workspace deps. agents-core depends on a small number of workspace
# packages; install everything to keep TypeScript imports resolvable.
RUN pnpm install --frozen-lockfile

# Pre-build the agents-core metadata so vitest can run without the postbuild step.
RUN pnpm -F @openai/agents-core prebuild

# Build dist for all workspace packages: vitest resolves cross-package imports
# (e.g. @openai/agents-core/_shims) via the published `exports` field, which
# points to the built dist/. Build once at image creation so test runs are fast.
RUN pnpm build

# Logs directory the test harness writes reward to.
RUN mkdir -p /logs/verifier
