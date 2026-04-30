FROM oven/bun:1.3.11

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout dc16013b4f0aa5e4d3eb433046965e1274da3990

# Minimal isolated install of just the deps needed by the migrated schemas:
#   effect@4.0.0-beta.48 (Schema, SchemaAST)
#   zod@4.1.8 (compat surface)
# We avoid `bun install` at the workspace root because the monorepo pulls
# hundreds of unrelated deps. Symlinking node_modules into packages/opencode
# lets Node-style resolution from the schema files find effect/zod, while
# tsconfig paths handle `@/util/*` -> `./src/*` resolution.
WORKDIR /minimal
RUN echo '{"name":"min","type":"module","dependencies":{"effect":"4.0.0-beta.48","zod":"4.1.8"}}' > package.json \
    && bun install --no-progress

RUN ln -s /minimal/node_modules /workspace/opencode/packages/opencode/node_modules

# Neutralise the package's bunfig.toml — its `preload = ["@opentui/solid/preload"]`
# entry exists for the TUI test fixtures and would force us to install all of
# opentui just to load three schema files. Tests in this task don't touch the
# TUI; replace with a minimal config that disables preloading.
RUN echo '' > /workspace/opencode/packages/opencode/bunfig.toml \
 && echo '' > /workspace/opencode/bunfig.toml

WORKDIR /workspace/opencode/packages/opencode

RUN mkdir -p /logs/verifier
