FROM node:22.13-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Pinned Python deps used by the verifier.
RUN pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

WORKDIR /workspace

# Shallow clone the apache/superset repository at the parent of the merge commit.
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout da371217ef689b07bce5a056a8aea0dffe5c3f5a

# Self-contained Node test harness: esbuild bundler + rison encoder.
# The harness exercises useDownloadScreenshot.ts with all React/redux/etc.
# imports replaced by stubs, then captures the URL passed to
# SupersetClient.post. No npm install of the full superset-frontend
# workspace is required.
COPY test_harness /opt/test_harness
WORKDIR /opt/test_harness
RUN npm install --no-audit --no-fund --omit=dev

WORKDIR /workspace/superset

RUN mkdir -p /logs/verifier
