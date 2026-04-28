FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/jentic-mini && \
    cd /workspace/jentic-mini && \
    git remote add origin https://github.com/jentic/jentic-mini.git && \
    git fetch --depth=1 origin 12adc64e065adafa9e2e3327f8e39b3bc1cd3915 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/jentic-mini
