FROM node:22.20.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# pytest + yaml + pytest-json-report for the test harness.
# pytest-json-report is consumed by test.sh to emit /logs/verifier/ctrf.json.
RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 pyyaml==6.0.2 pytest-json-report==1.5.0

# Install pnpm directly (pinned to repo's packageManager version).
# corepack signing-key validation is unstable on this base image, so we
# skip it.
RUN npm install -g pnpm@10.33.0 \
    && pnpm --version

WORKDIR /workspace

# Clone repo at the base commit (parent of the merge commit)
RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git \
    && cd openai-agents-js \
    && git checkout 4b99d53d256dfb50e9a220e5b53d2c933764bffc

WORKDIR /workspace/openai-agents-js

# Install workspace deps (cached in image)
RUN pnpm install --frozen-lockfile

# Pre-build the workspace using tsc-multi (produces both .js + .mjs outputs
# per the package exports maps). vitest needs the .mjs builds for the
# `@openai/agents-core/_shims` subpath import used by the tracing module.
RUN pnpm run build:ci

RUN mkdir -p /logs/verifier

CMD ["/bin/bash"]
