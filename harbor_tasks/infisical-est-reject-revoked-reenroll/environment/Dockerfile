FROM node:22.22.2-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_ENV=test

# Build deps for native node modules (re2, bcrypt, argon2, msgpackr-extract, cpu-features),
# git for cloning, ca-certificates for HTTPS, python3/pytest as the test harness.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates=20230311+deb12u1 \
        build-essential=12.9 \
        python3=3.11.2-1+b1 \
        python3-pip=23.0.1+dfsg-1 \
        pkg-config=1.8.1-1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4

# Clone repo at base commit (parent of merge commit for PR #6163)
ARG REPO_URL=https://github.com/Infisical/infisical.git
ARG BASE_COMMIT=d3b69683c96a7f67671af07e7cb02a131b04586b
WORKDIR /workspace
RUN git clone --filter=blob:none "$REPO_URL" infisical \
    && cd infisical \
    && git checkout "$BASE_COMMIT" \
    && git config user.email "task@example.com" \
    && git config user.name "Task Runner"

# Install backend npm deps (this builds re2, bcrypt, argon2, msgpackr-extract, cpu-features
# native bindings via node-gyp). Skip pkcs11js / odbc by ignoring scripts? No — those also
# fail unless we have all build deps. We do, so let postinstall run normally.
WORKDIR /workspace/infisical/backend
RUN npm install --prefer-offline --no-audit --no-fund 2>&1 | tail -5 || true

# Verify re2 native binding loaded successfully — without this, vitest can't import the
# service-under-test.
RUN node -e "require('re2'); console.log('re2 OK')"

WORKDIR /workspace/infisical
RUN mkdir -p /logs/verifier
