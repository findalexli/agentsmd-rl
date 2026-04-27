FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.32.1 --activate

WORKDIR /workspace

RUN git init /workspace/agents-js && \
    cd /workspace/agents-js && \
    git remote add origin https://github.com/openai/openai-agents-js.git && \
    git fetch --depth=1 origin 7a9ed1c12c590f76fbfea12c48c4b8c514d31ac1 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/agents-js

RUN pnpm install --frozen-lockfile

# Vitest resolves intra-monorepo aliases (e.g. @openai/agents-core/_shims) via
# the package's `exports` map, which points at `dist/`. Pre-build so test
# discovery succeeds even before the agent rebuilds.
RUN pnpm build

RUN pip3 install --no-cache-dir --break-system-packages \
        pytest==8.3.4 \
        pyyaml==6.0.2

RUN mkdir -p /logs/verifier

CMD ["bash"]
