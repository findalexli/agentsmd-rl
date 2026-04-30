FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/netsuite-suitecloud-sdk && \
    cd /workspace/netsuite-suitecloud-sdk && \
    git remote add origin https://github.com/oracle/netsuite-suitecloud-sdk.git && \
    git fetch --depth=1 origin e3bba7c6a75e85c5377642669d67837e642888f4 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/netsuite-suitecloud-sdk
