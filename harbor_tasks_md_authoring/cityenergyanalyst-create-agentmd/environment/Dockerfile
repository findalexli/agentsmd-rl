FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cityenergyanalyst && \
    cd /workspace/cityenergyanalyst && \
    git remote add origin https://github.com/architecture-building-systems/CityEnergyAnalyst.git && \
    git fetch --depth=1 origin 608eed59ac8c82866fe3b788552c64548eabedcb && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cityenergyanalyst
