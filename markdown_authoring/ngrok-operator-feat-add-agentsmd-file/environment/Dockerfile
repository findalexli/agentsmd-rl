FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/ngrok-operator && \
    cd /workspace/ngrok-operator && \
    git remote add origin https://github.com/ngrok/ngrok-operator.git && \
    git fetch --depth=1 origin df17bdbcc015292941c31439b23f420d835d9334 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ngrok-operator
