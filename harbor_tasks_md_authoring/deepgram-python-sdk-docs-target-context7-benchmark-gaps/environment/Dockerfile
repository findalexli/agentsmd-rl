FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/deepgram-python-sdk && \
    cd /workspace/deepgram-python-sdk && \
    git remote add origin https://github.com/deepgram/deepgram-python-sdk.git && \
    git fetch --depth=1 origin e1b01fe1212040d59aca2761c5b97c432c321052 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/deepgram-python-sdk
