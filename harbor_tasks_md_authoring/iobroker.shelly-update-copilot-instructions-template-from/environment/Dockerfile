FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/iobroker.shelly && \
    cd /workspace/iobroker.shelly && \
    git remote add origin https://github.com/iobroker-community-adapters/ioBroker.shelly.git && \
    git fetch --depth=1 origin bd5ccedbe122f9d633230291a352ce3d8407677f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/iobroker.shelly
