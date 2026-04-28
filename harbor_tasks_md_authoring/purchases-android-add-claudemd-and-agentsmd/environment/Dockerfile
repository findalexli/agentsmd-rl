FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/purchases-android && \
    cd /workspace/purchases-android && \
    git remote add origin https://github.com/RevenueCat/purchases-android.git && \
    git fetch --depth=1 origin 4db1dc7b43c90de8a2930ae8ca5437d5c71fbbfd && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/purchases-android
