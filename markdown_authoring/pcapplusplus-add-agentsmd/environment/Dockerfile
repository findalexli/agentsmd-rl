FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/pcapplusplus && \
    cd /workspace/pcapplusplus && \
    git remote add origin https://github.com/seladb/PcapPlusPlus.git && \
    git fetch --depth=1 origin 3d90f4493aac177288cf7d3c616c9d0815ef6043 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/pcapplusplus
