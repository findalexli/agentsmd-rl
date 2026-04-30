FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/trucksim-telemetry && \
    cd /workspace/trucksim-telemetry && \
    git remote add origin https://github.com/kniffen/TruckSim-Telemetry.git && \
    git fetch --depth=1 origin b3f39e9d7a868ed2911e3cf784ec47294839ea5d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/trucksim-telemetry
