FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/firebase-ios-sdk && \
    cd /workspace/firebase-ios-sdk && \
    git remote add origin https://github.com/firebase/firebase-ios-sdk.git && \
    git fetch --depth=1 origin 6e0fdaece66649b46e5ab55aa2f5810fc0e88ec1 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/firebase-ios-sdk
