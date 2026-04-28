FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/googleads-mobile-android-examples && \
    cd /workspace/googleads-mobile-android-examples && \
    git remote add origin https://github.com/googleads/googleads-mobile-android-examples.git && \
    git fetch --depth=1 origin 3a5262c1b461b29b3c38117473c7e2b1cc26c90b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/googleads-mobile-android-examples
