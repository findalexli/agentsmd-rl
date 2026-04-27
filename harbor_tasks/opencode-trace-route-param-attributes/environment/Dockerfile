FROM oven/bun:1.3.13-debian

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
        pytest==8.3.4

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git opencode \
    && cd opencode \
    && git checkout cded68a2e2e233b8026c50408771b25d0f4e9682

WORKDIR /workspace/opencode/packages/opencode

# Install only the packages/opencode workspace deps. Skip native postinstall
# scripts (fix-node-pty, husky) that require platform-specific binaries we
# don't need to test the trace.ts module.
RUN cd /workspace/opencode \
    && bun install --ignore-scripts --no-summary 2>&1 | tail -20

RUN mkdir -p /logs/verifier
