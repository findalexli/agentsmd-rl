FROM oven/bun:1.3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.* \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pyenv \
    && /opt/pyenv/bin/pip install --no-cache-dir \
        pytest==8.3.4
ENV PATH="/opt/pyenv/bin:${PATH}"

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout caaddf096424193ef3cba4bf2a8f9ae6876915bc

WORKDIR /workspace/opencode

ENV BUN_INSTALL_CACHE_DIR=/root/.bun-install-cache
ENV HUSKY=0
RUN cd /workspace/opencode \
    && bun install --frozen-lockfile --ignore-scripts 2>&1 | tail -20

RUN mkdir -p /logs/verifier
