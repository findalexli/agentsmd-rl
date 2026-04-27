FROM node:22.21.1-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1

RUN corepack enable

WORKDIR /workspace

ARG BASE_COMMIT=5a9c6ecd7559ee8c7adbe30fb4b0894e369d144b

RUN git init storybook \
    && cd storybook \
    && git remote add origin https://github.com/storybookjs/storybook.git \
    && git -c protocol.version=2 fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout FETCH_HEAD \
    && git config user.email "scaffold@local" \
    && git config user.name "scaffold"

WORKDIR /workspace/storybook

RUN corepack prepare yarn@4.10.3 --activate

ENV YARN_ENABLE_GLOBAL_CACHE=false
ENV YARN_NM_MODE=hardlinks-local
ENV NODE_OPTIONS=--max_old_space_size=4096

RUN yarn install --network-timeout 600000

# Compile the `storybook` core package so vitest can resolve `storybook/internal/*`
# imports via the dist outputs (the test files import from those subpaths).
RUN yarn nx compile core 2>&1 | tail -5 || true
RUN test -f /workspace/storybook/code/core/dist/common/index.js \
    && echo "core compiled OK" \
    || (echo "core not compiled" && exit 1)

# Disable the storybook-tests vitest project (requires @storybook/addon-vitest
# which isn't built); CI-only project, irrelevant for the unit tests we run.
RUN sed -i 's|projects.push.*vitest.config.storybook.ts.*|// disabled by scaffold|' code/vitest.config.ts

# Apply the test-file portion of the gold patch so the failing tests appear
# in the repo (snapshot tests + new "only emits once" test). The agent then
# fixes source code to make these tests pass.
COPY tests_only.patch /tmp/tests_only.patch
RUN git apply /tmp/tests_only.patch && rm /tmp/tests_only.patch

RUN mkdir -p /logs/verifier
