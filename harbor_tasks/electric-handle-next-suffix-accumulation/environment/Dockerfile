FROM node:22.13.0-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CI=true

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Pin pnpm to the version declared in the repo's packageManager field.
# Install via npm directly to sidestep corepack signature verification flakes.
RUN npm install -g pnpm@10.12.1

# Pin pytest at install time (test.sh installs pinned versions; this just keeps
# the image self-contained for offline runs).
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1 \
        pyyaml==6.0.2
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /workspace

# Clone the Electric monorepo at the base commit (parent of the merge).
ARG REPO_URL=https://github.com/electric-sql/electric.git
ARG BASE_COMMIT=deb2a61614678fac029773a56b618382fe5b70f2
RUN git clone --filter=blob:none "${REPO_URL}" electric \
 && cd electric \
 && git checkout "${BASE_COMMIT}" \
 && git config --global user.email "task@bench.local" \
 && git config --global user.name "task"

WORKDIR /workspace/electric

# Restrict the workspace to just the typescript-client package so pnpm install
# doesn't try to bootstrap the dozens of other monorepo packages (some of which
# require Elixir/Erlang). The patches/ directory is preserved because the root
# pnpm config patches `@microsoft/fetch-event-source`.
RUN printf 'packages:\n  - "packages/typescript-client"\n' > pnpm-workspace.yaml

# Use pnpm to install dependencies for the typescript-client package only.
# --ignore-scripts skips lifecycle scripts in deps (some try to download
# native binaries we don't need for unit tests).
RUN pnpm install --no-frozen-lockfile --ignore-scripts \
        --filter "@electric-sql/client..."

RUN mkdir -p /logs/verifier
