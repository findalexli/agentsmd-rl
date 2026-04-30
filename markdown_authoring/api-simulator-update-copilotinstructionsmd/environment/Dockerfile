FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/api-simulator && \
    cd /workspace/api-simulator && \
    git remote add origin https://github.com/counterfact/api-simulator.git && \
    git fetch --depth=1 origin 2673e86e66f4cc34b4151396702096d4d2391198 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/api-simulator
