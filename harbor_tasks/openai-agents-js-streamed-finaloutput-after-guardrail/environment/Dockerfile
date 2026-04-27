FROM node:22.14-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PNPM_HOME=/root/.local/share/pnpm \
    PATH=/root/.local/share/pnpm:$PATH \
    CI=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.4.1 --activate

WORKDIR /workspace

RUN git init /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git remote add origin https://github.com/openai/openai-agents-js.git && \
    git fetch --depth=1 origin 1227865cd903f875eab4908fbff8c41a033b9275 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/openai-agents-js

RUN pnpm install --frozen-lockfile

# Build all packages so vitest can resolve `@openai/agents-core/_shims`
# via the published `exports` map. (Tests still load TS sources directly via
# the tsconfig.test.json `paths` mapping; dist is only needed for the
# subpath-export resolution.)
RUN pnpm build

# Pytest harness. Pinned for determinism.
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH=/opt/venv/bin:$PATH

RUN mkdir -p /logs/verifier

CMD ["bash"]
