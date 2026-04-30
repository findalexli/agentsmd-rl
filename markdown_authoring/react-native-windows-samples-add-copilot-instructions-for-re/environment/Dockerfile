FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/react-native-windows-samples && \
    cd /workspace/react-native-windows-samples && \
    git remote add origin https://github.com/microsoft/react-native-windows-samples.git && \
    git fetch --depth=1 origin f1fecd43f3ca101bca6adcfa3a45b4af9c687b9a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/react-native-windows-samples
