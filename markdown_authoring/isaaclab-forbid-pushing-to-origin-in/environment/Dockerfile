FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/isaaclab && \
    cd /workspace/isaaclab && \
    git remote add origin https://github.com/isaac-sim/IsaacLab.git && \
    git fetch --depth=1 origin 0c565d63a9e6c6169cdec1ae13eaf000487dc666 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/isaaclab
