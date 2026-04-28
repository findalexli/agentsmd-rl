FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/bitbox02-firmware && \
    cd /workspace/bitbox02-firmware && \
    git remote add origin https://github.com/BitBoxSwiss/bitbox02-firmware.git && \
    git fetch --depth=1 origin bea3a85a5939f5f761834ef68b7011ff1ef2be6a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bitbox02-firmware
