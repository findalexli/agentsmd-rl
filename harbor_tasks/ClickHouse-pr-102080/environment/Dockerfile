FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    coreutils \
    gawk \
    grep \
    python3 \
    python3-pip \
    patch \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

# Clone ClickHouse repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=cf5fb461472203d56bb0c169a61d194dd97fc2f2
RUN git init /workspace/ClickHouse && \
    cd /workspace/ClickHouse && \
    git remote add origin https://github.com/ClickHouse/ClickHouse.git && \
    git fetch --depth=1 origin cf5fb461472203d56bb0c169a61d194dd97fc2f2 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ClickHouse

# Install pytest for test runner
RUN pip3 install pytest --break-system-packages
