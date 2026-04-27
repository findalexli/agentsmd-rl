FROM oven/bun:1.3.11

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 \
      python3-pip \
      python3-venv \
      git \
      ca-certificates \
      curl \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages \
      pytest==8.3.4 \
      pytest-json-ctrf==0.3.5

ENV HUSKY=0 \
    CI=1 \
    BUN_INSTALL_CACHE_DIR=/tmp/bun-cache

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout f592c3846b285a53d9f657d1eb57f124d5b9b18b

WORKDIR /workspace/opencode
RUN bun install --ignore-scripts || bun install --ignore-scripts

RUN mkdir -p /logs/verifier
