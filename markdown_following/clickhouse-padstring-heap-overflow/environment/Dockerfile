# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Clone ClickHouse repo (sparse checkout for the files we need)
WORKDIR /workspace
RUN git clone --depth=1 --filter=blob:none --sparse \
    https://github.com/ClickHouse/ClickHouse.git && \
    cd ClickHouse && \
    git sparse-checkout set src/Functions tests/queries/0_stateless && \
    git fetch --depth=1 origin 73ad233a01a81190b2a45b820878e54c36a9a22c && \
    git checkout 73ad233a01a81190b2a45b820878e54c36a9a22c

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ClickHouse
