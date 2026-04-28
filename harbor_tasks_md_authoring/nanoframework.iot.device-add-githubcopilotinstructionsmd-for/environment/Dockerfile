FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/nanoframework.iot.device && \
    cd /workspace/nanoframework.iot.device && \
    git remote add origin https://github.com/nanoframework/nanoFramework.IoT.Device.git && \
    git fetch --depth=1 origin 31ea014d167823f7ab57e7fa571fec3bcd7954ce && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/nanoframework.iot.device
