# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest and pyyaml
RUN pip install pytest pyyaml

# Clone ClickHouse repo (sparse checkout for the files we need)
WORKDIR /workspace
RUN git clone --depth=1 --filter=blob:none --sparse \
    https://github.com/ClickHouse/ClickHouse.git && \
    cd ClickHouse && \
    git sparse-checkout set src/Functions/UserDefined && \
    git fetch --depth=1 origin 255e0773744e57c9b6435e713a6f8417ee690ea5 && \
    git checkout 255e0773744e57c9b6435e713a6f8417ee690ea5

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
