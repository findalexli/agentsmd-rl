FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/riscv-unified-db && \
    cd /workspace/riscv-unified-db && \
    git remote add origin https://github.com/riscv/riscv-unified-db.git && \
    git fetch --depth=1 origin d7e53780da2abc92f9832228b7751259628b843a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/riscv-unified-db
