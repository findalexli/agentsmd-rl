FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/swiftformat && \
    cd /workspace/swiftformat && \
    git remote add origin https://github.com/nicklockwood/SwiftFormat.git && \
    git fetch --depth=1 origin b1d6cff72150e181cf6befe1814b8ef74e471be0 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/swiftformat
