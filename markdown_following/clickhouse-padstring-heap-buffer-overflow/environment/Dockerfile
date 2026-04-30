FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install --break-system-packages pytest

# Clone ClickHouse repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/ClickHouse/ClickHouse.git

WORKDIR /workspace/ClickHouse
# Fetch base commit (parent of merge)
RUN git fetch --depth=1 origin 37d84eba23c7b04f5b8e48b5b1742e7027cff555 && \
    git checkout 37d84eba23c7b04f5b8e48b5b1742e7027cff555

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
