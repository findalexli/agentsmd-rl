FROM oven/bun:1.3.13

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-ctrf==0.3.5

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git \
 && cd opencode \
 && git checkout 1e439b8226a66dcec0d65751f5cdb50a2b7bc979

WORKDIR /workspace/opencode

RUN bun install --frozen-lockfile

RUN mkdir -p /logs/verifier
