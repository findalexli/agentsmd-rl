FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    unzip \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install bun (pinned binary release, no install script — deterministic)
ARG BUN_VERSION=1.3.11
RUN set -eux; \
    arch="$(uname -m)"; \
    case "$arch" in \
        x86_64)  bun_arch="x64"  ;; \
        aarch64) bun_arch="aarch64" ;; \
        *) echo "unsupported arch: $arch"; exit 1 ;; \
    esac; \
    curl -fsSL "https://github.com/oven-sh/bun/releases/download/bun-v${BUN_VERSION}/bun-linux-${bun_arch}.zip" -o /tmp/bun.zip; \
    unzip -q /tmp/bun.zip -d /tmp/bun; \
    mv /tmp/bun/bun-linux-${bun_arch}/bun /usr/local/bin/bun; \
    rm -rf /tmp/bun /tmp/bun.zip; \
    chmod +x /usr/local/bin/bun; \
    /usr/local/bin/bun --version

# Test runner deps
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.4.1

# Clone repo at base commit (parent of merge commit 326471a25c50cb83d33e6b327bc88faf38a4db11)
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/anomalyco/opencode.git opencode \
    && cd opencode \
    && git config advice.detachedHead false \
    && git checkout 6405e3a7b12d49ade2f251360d221999836ccc02

# Install zod for the probe scripts at the workspace root so bun's node_modules
# walk-up resolution finds it from any file under /workspace/opencode/
WORKDIR /workspace
RUN echo '{"name":"probe-deps","type":"module","dependencies":{"zod":"4.1.8"}}' > package.json \
    && /usr/local/bin/bun install \
    && rm package.json

# Install monorepo dependencies so typecheck and unit tests can run
RUN cd /workspace/opencode && bun install

# Verifier output dir
RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode
