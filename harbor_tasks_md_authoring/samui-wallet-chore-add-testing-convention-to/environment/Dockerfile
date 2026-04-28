FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest==8.3.4 pyyaml==6.0.2

WORKDIR /workspace
RUN git init /workspace/samui-wallet && \
    cd /workspace/samui-wallet && \
    git remote add origin https://github.com/samui-build/samui-wallet.git && \
    git fetch --depth=1 origin 16ebdc535cff0807dbf006de5cc6fbb08b1ea96b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/samui-wallet
