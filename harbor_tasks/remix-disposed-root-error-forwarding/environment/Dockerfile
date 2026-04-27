FROM mcr.microsoft.com/playwright:v1.57.0-noble

# Skip pnpm postinstall hook that auto-installs playwright (already installed in base image)
ENV CI=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-venv \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm matching the repo's packageManager spec
RUN npm install -g pnpm@10.26.0 corepack@0.34.0

# Create a python venv for pytest so we can `pip install` without --break-system-packages
RUN python3 -m venv /opt/pyenv && \
    /opt/pyenv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH="/opt/pyenv/bin:${PATH}"

WORKDIR /workspace

# Clone repo at base commit (parent of merge commit for PR #11113)
ARG REPO_URL=https://github.com/remix-run/remix.git
ARG BASE_COMMIT=5ce4b49540814294c08af920bd2b582881349f29
RUN git clone --filter=blob:none "${REPO_URL}" remix && \
    cd remix && \
    git checkout "${BASE_COMMIT}" && \
    git config user.email "task@local" && \
    git config user.name "Task Runner"

WORKDIR /workspace/remix

# Install dependencies. CI=1 skips the postinstall playwright auto-install
# (the playwright base image already has chromium installed).
RUN pnpm install --frozen-lockfile

# Use playwright already installed in /ms-playwright; reset env so vitest picks it up
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /workspace/remix/packages/component

RUN mkdir -p /logs/verifier
