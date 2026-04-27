FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pytest in a venv (Debian PEP 668 prevents global pip)
RUN python3 -m venv /opt/pytest-venv \
 && /opt/pytest-venv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5
ENV PATH="/opt/pytest-venv/bin:${PATH}"

WORKDIR /workspace

# Clone OpenHands at base commit (only frontend tree is needed for these tests)
RUN git clone --filter=blob:none --no-checkout https://github.com/OpenHands/OpenHands.git openhands \
 && cd openhands \
 && git -c advice.detachedHead=false checkout fd014e8e23fa631b1667fe25929a149c85154519 -- \
        frontend AGENTS.md README.md .gitattributes \
 && git -c user.email=task@scaffold -c user.name=task add -A \
 && git -c user.email=task@scaffold -c user.name=task commit -m "base" >/dev/null

WORKDIR /workspace/openhands/frontend

# Pre-install node_modules at build time so tests run without network
RUN npm install --no-audit --no-fund --prefer-offline \
 && npm cache clean --force

# Pre-generate the i18n declaration so the first vitest run doesn't have to
RUN npm run make-i18n

WORKDIR /workspace/openhands

RUN mkdir -p /logs/verifier
