FROM rust:1.85-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    libclang-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the sui repository at the base commit
ARG BASE_COMMIT=08500756541c6fd66c81a59d1af1d819e997a189
RUN git clone --filter=blob:none --depth=50 https://github.com/MystenLabs/sui.git sui && \
    cd sui && \
    git checkout ${BASE_COMMIT}

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/sui
