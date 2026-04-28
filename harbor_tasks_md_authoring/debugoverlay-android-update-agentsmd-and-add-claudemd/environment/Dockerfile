FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/debugoverlay-android && \
    cd /workspace/debugoverlay-android && \
    git remote add origin https://github.com/Manabu-GT/DebugOverlay-Android.git && \
    git fetch --depth=1 origin d7d4312d5d3c7db3c4b5568955aa378e49123add && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/debugoverlay-android
