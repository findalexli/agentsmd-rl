FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/cultivation-world-simulator && \
    cd /workspace/cultivation-world-simulator && \
    git remote add origin https://github.com/4thfever/cultivation-world-simulator.git && \
    git fetch --depth=1 origin 4a4c45c42856172b36f07072ff09f2d82d131745 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/cultivation-world-simulator
