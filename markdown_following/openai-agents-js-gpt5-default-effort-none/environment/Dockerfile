FROM node:22.13.1-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm directly (corepack signature key in node:22.11 ships expired,
# preventing `corepack prepare` from fetching newer pnpm versions).
RUN npm install -g pnpm@10.28.0

RUN pip3 install --break-system-packages \
        pytest==8.3.4

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js \
    && cd /workspace/openai-agents-js \
    && git checkout 720a7071780b059f3f98b9cbd7be37cbda0a638a

WORKDIR /workspace/openai-agents-js

RUN pnpm install --frozen-lockfile

# The agents-core `./_shims` export points at compiled bundles in dist/, so
# vitest cannot resolve it without a full build (tsc-multi produces both
# `.js` (CJS) and `.mjs` (ESM) variants needed by the package's `exports`
# map). Build all packages once at image build time so tests can run offline;
# the agent will rebuild after edits if their changes affect compiled output.
RUN pnpm build

RUN mkdir -p /logs/verifier

CMD ["bash"]
