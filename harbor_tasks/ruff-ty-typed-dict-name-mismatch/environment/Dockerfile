FROM rust:1.94.1-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=never \
    RUST_BACKTRACE=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        libssl-dev \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5 \
        pyyaml==6.0.2

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git ruff \
    && cd ruff \
    && git checkout 6728820252f31969cba8258c32b1fe7e7162d5d9

WORKDIR /workspace/ruff

RUN cargo build --bin ty 2>&1 | tail -20 \
    && rm -rf target/debug/incremental \
    && find target/debug/deps -name '*.rlib' -size +0 | wc -l \
    && du -sh target

RUN mkdir -p /logs/verifier

CMD ["bash"]
