FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/stripe-android && \
    cd /workspace/stripe-android && \
    git remote add origin https://github.com/stripe/stripe-android.git && \
    git fetch --depth=1 origin cc32f6913ba7442da3afa1584f7b2f51873ead0b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/stripe-android
