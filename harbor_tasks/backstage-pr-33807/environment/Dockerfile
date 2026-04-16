FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages pytest

RUN git config --global --add safe.directory '*'

WORKDIR /workspace

# Clone the base commit of the backstage repo (with the bug)
RUN git clone --filter=blob:none --depth=1 \
    --branch=master \
    https://github.com/backstage/backstage.git \
    /workspace/backstage && \
    cd /workspace/backstage && \
    git checkout 5b1ba4ee3ece1f6a33b2b4c6c8ad77cdc2b52a83