FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/luisacompute && \
    cd /workspace/luisacompute && \
    git remote add origin https://github.com/LuisaGroup/LuisaCompute.git && \
    git fetch --depth=1 origin a2f118e0fc065ad70e624eef7406140efa6001cf && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/luisacompute
