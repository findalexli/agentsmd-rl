FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PNPM_HOME=/root/.local/share/pnpm \
    PATH=/root/.local/share/pnpm:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN pip install --no-cache-dir pytest==8.3.4

RUN corepack enable && corepack prepare pnpm@10.30.3 --activate

WORKDIR /workspace
RUN git init /workspace/agents-js && \
    cd /workspace/agents-js && \
    git remote add origin https://github.com/openai/openai-agents-js.git && \
    git fetch --depth=1 origin 4e6b3fbd3355709831a1bb64472b3c947b694690 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/agents-js

RUN pnpm install --frozen-lockfile

# Full root build runs tsc-multi which produces both `.js` (CJS) and `.mjs`
# (ESM) outputs. The package's exports field maps both, and vitest's resolver
# needs the `.mjs` files for `@openai/agents-core/_shims` to load. The
# package-level `pnpm -F @openai/agents-core build` would only produce one
# extension and is not sufficient.
RUN pnpm build

RUN mkdir -p /logs/verifier
