FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun v1.3.10 (pinned binary from GitHub release)
RUN curl -fsSL -o /tmp/bun.zip \
    https://github.com/oven-sh/bun/releases/download/bun-v1.3.10/bun-linux-x64.zip \
    && unzip /tmp/bun.zip -d /tmp/bun-extract \
    && cp /tmp/bun-extract/bun-linux-x64/bun /usr/local/bin/bun \
    && chmod +x /usr/local/bin/bun \
    && rm -rf /tmp/bun.zip /tmp/bun-extract

ENV PATH="/usr/local/bin:$PATH"

RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    pyyaml==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none --no-checkout \
    https://github.com/anomalyco/opencode.git opencode \
    && cd opencode \
    && git config advice.detachedHead false \
    && git checkout dcb17c6a678918ce0786640729fcc8cd8adb1746

RUN cd /workspace/opencode && bun install

RUN mkdir -p /logs/verifier
