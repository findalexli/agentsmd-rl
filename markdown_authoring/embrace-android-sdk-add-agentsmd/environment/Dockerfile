FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/embrace-android-sdk && \
    cd /workspace/embrace-android-sdk && \
    git remote add origin https://github.com/embrace-io/embrace-android-sdk.git && \
    git fetch --depth=1 origin dd56dd3e3cd10414f9c73bd17685bda3a30272f7 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/embrace-android-sdk
