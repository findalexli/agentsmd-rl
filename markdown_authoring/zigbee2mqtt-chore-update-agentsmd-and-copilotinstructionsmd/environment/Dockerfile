FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/zigbee2mqtt && \
    cd /workspace/zigbee2mqtt && \
    git remote add origin https://github.com/Koenkk/zigbee2mqtt.git && \
    git fetch --depth=1 origin 5f893c56573307e1aaeb6cb96d88310b138348af && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/zigbee2mqtt
