FROM node:22.18.0-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CI=1
ENV NODE_OPTIONS=--max-old-space-size=4096

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    python3-venv \
    curl \
  && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv \
  && /opt/venv/bin/pip install --no-cache-dir \
       pytest==8.3.4
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /workspace

ARG REPO_URL=https://github.com/OpenHands/OpenHands.git
ARG BASE_COMMIT=b357c0c3bb6d0e55c87ecea2262db7efe7c9d896
RUN git clone --filter=blob:none "${REPO_URL}" OpenHands \
  && cd OpenHands \
  && git checkout "${BASE_COMMIT}"

WORKDIR /workspace/OpenHands

# Pre-stage mock + test changes from PR (testing infrastructure, not the fix).
# Agent's task is to fix the source files (sdk-section-page.tsx, llm-settings.tsx).
COPY infra_patch.diff /tmp/infra_patch.diff
RUN git apply --whitespace=nowarn /tmp/infra_patch.diff && rm /tmp/infra_patch.diff

WORKDIR /workspace/OpenHands/frontend

# Run the i18n declaration generation step that the test pipeline expects.
RUN npm ci --no-audit --no-fund --prefer-offline 2>&1 | tail -50 || \
    npm install --no-audit --no-fund 2>&1 | tail -50

RUN npm run make-i18n

RUN mkdir -p /logs/verifier

WORKDIR /workspace/OpenHands
