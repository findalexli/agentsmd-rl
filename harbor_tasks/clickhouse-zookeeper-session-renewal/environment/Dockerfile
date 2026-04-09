FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    clang-16 \
    llvm-16 \
    libc++-dev \
    libc++abi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

# Clone ClickHouse at base commit with shallow clone
WORKDIR /workspace
RUN git clone --depth=1 --filter=blob:none https://github.com/ClickHouse/ClickHouse.git ClickHouse && \
    cd ClickHouse && \
    git fetch --depth=1 origin a3c77899d3f826cfdc879ce9c276dd5f019cb46d && \
    git checkout a3c77899d3f826cfdc879ce9c276dd5f019cb46d

WORKDIR /workspace/ClickHouse

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages
