FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/edgeai-for-beginners && \
    cd /workspace/edgeai-for-beginners && \
    git remote add origin https://github.com/microsoft/edgeai-for-beginners.git && \
    git fetch --depth=1 origin 4125a2106904c4d966042966f5990f526e78099b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/edgeai-for-beginners
